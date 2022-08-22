import os
import re
import shlex
import sys
import traceback
from itertools import chain
from shutil import which
from string import ascii_letters
from subprocess import PIPE, Popen

import gdb
from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import ANSI, FormattedText
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.output import create_output
# from prompt_toolkit.shortcuts import CompleteStyle

# global variables
HAS_FZF = which('fzf') is not None
HISTORY_FILENAME = '.gdb_history'
# This sucks, but there's not a GDB API for checking dont-repeat now.
# I just collect some common used commands which should not be repeated.
# If you have some user-define function, add your command into the list manually.
# If you found a command should/shouldn't in this list, please let me know on the issue page, thanks!
DONT_REPEAT = [
    # original GDB
    'attach',
    'run', 'r',
    'detach',
    'help',
    'complete',
    'quit', 'q',
    # for GEF
    'theme',
    'canary',
    'functions',
    'gef',
    'tmux-setup',
    # your functions:
    # 'foo',
    # 'bar'
]
try:
    from geprc import BINDINGS
except ImportError:
    from prompt_toolkit.key_binding import KeyBindings

    BINDINGS = KeyBindings()


# function for logging
def print_info(s):
    print_formatted_text(FormattedText([('#00FFFF', s)]), file=sys.__stdout__)


def print_warning(s):
    print_formatted_text(FormattedText([('#FFCC00', s)]), file=sys.__stdout__)


# key binding for fzf history search
if HAS_FZF:
    @BINDINGS.add('c-r')
    def _(event):
        """ Reverse search history with fzf. """

        def f():
            query = shlex.quote(event.app.current_buffer.document.text_before_cursor)
            global HISTORY_FILENAME
            if not os.path.exists(HISTORY_FILENAME):
                # just create an empty file
                with open(HISTORY_FILENAME, 'w'):
                    pass
            fzf_cmd = [f"awk '!seen[$0]++' {shlex.quote(HISTORY_FILENAME)}"]
            fzf_cmd += [f"fzf --tiebreak=index --no-multi --height=40% --layout=reverse --tac --query={query}"]
            fzf_cmd = '|'.join(fzf_cmd)
            p = Popen(fzf_cmd, shell=True, stdout=PIPE, text=True)
            stdout, _ = p.communicate()
            if stdout:
                event.app.current_buffer.document = Document()  # clear buffer
                event.app.current_buffer.insert_text(stdout.strip())

        run_in_terminal(f)
else:
    print_warning('Install fzf for better experience with GEP')


class GDBHistory(FileHistory):
    """
    Manage your GDB History
    """

    def __init__(self, filename, ignore_duplicates=False):
        self.ignore_duplicates = ignore_duplicates
        super().__init__(filename=filename)

    def load_history_strings(self):
        temp_strings = []

        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                for line in f:
                    line = line.decode('utf-8')
                    string = line.strip()
                    temp_strings.append(string)

        strings = []
        for string in reversed(temp_strings):
            if self.ignore_duplicates and string in strings:
                continue
            if string:
                strings.append(string)
        return strings

    def store_string(self, string):
        with open(self.filename, 'ab') as f:
            f.write(string.strip().encode() + b'\n')


class GDBCompleter(Completer):
    """
    Completer of GDB
    """

    def __init__(self):
        super().__init__()

    def get_completions(self, document, complete_event):
        completions_limit = gdb.parameter('max-completions')
        if completions_limit == -1:
            completions_limit = 0xffffffff
        if completions_limit == 0:
            return
        if document.text_before_cursor.strip() and document.text_before_cursor[-1].isspace():
            # fuzzing all possible commands if the text before cursor endswith space
            all_completions = []
            for c in ascii_letters + "_-":
                if completions_limit <= 0:
                    break
                completions = gdb.execute(f"complete {document.text_before_cursor + c}", to_string=True).split('\n')
                completions.pop()  # remove empty line
                if completions and ' *** List may be truncated, max-completions reached. ***' == completions[-1]:
                    completions.pop()
                all_completions = chain(all_completions, completions[:completions_limit])
                completions_limit -= len(completions)
        else:
            all_completions = gdb.execute(f'complete {document.text_before_cursor}', to_string=True).split('\n')
            all_completions.pop()  # remove empty line
            if all_completions and ' *** List may be truncated, max-completions reached. ***' == all_completions[-1]:
                all_completions.pop()
        for completion in all_completions:
            display_meta = None
            if ' ' not in completion:
                # raw completion may be a command, try to show its description
                try:
                    display_meta = gdb.execute(f'help {completion}', to_string=True).strip() or None
                except gdb.error:
                    # this is not a command
                    pass
            # remove some prefix of raw completion
            completion = completion.replace(document.text_before_cursor.lstrip(), '')
            # display readable completion based on the text before cursor
            display = re.split(r'\W+', document.text_before_cursor)[-1] + completion
            yield Completion(completion, display=display, display_meta=display_meta)


class GDBConsoleWrapper:
    """
    Wrapper of original GDB console
    """

    def __init__(self):
        old_prompt_hook = gdb.prompt_hook

        def prompt_until_exit(current_prompt):
            gdb.prompt_hook = old_prompt_hook  # retrieve old prompt hook 
            print_info('GEP is running now!')
            history_on = gdb.parameter('history save')
            if history_on:
                global HISTORY_FILENAME
                HISTORY_FILENAME = gdb.parameter('history filename')
                is_ignore_duplicates = -1 == gdb.parameter('history remove-duplicates')
                gdb_history = GDBHistory(HISTORY_FILENAME, ignore_duplicates=is_ignore_duplicates)
            else:
                print_warning('`set history save on` for better experience with GEP')
                gdb_history = InMemoryHistory()
            session = PromptSession(
                history=gdb_history,
                enable_history_search=True,
                auto_suggest=AutoSuggestFromHistory(),
                completer=GDBCompleter(),
                # TODO: Add a parameter to switch complete style
                # complete_style=CompleteStyle.MULTI_COLUMN, # the looking is not good for me
                complete_while_typing=False,
                key_bindings=BINDINGS,
                output=create_output(stdout=sys.__stdout__)
            )
            while True:
                try:
                    # emulate the original prompt
                    prompt_string = gdb.prompt_hook(current_prompt) if gdb.prompt_hook else None
                    if prompt_string is None:  # prompt string is set by gdb command
                        prompt_string = gdb.parameter('prompt')
                    prompt_string = prompt_string.replace('\001', '').replace('\002', '')  # fix for ANSI prompt
                    gdb_cmd = session.prompt(ANSI(prompt_string))
                    if not gdb_cmd.strip():
                        gdb_cmd_list = gdb_history.get_strings()
                        if gdb_cmd_list:
                            previous_gdb_cmd = gdb_cmd_list[-1]
                            if previous_gdb_cmd.split() and previous_gdb_cmd.split()[0] not in DONT_REPEAT:
                                gdb_cmd = previous_gdb_cmd
                    gdb.execute(gdb_cmd, from_tty=True)
                except gdb.error as e:
                    print(e)
                except (EOFError, KeyboardInterrupt):
                    gdb.execute('quit')
                except Exception as e:
                    print(e)
                    traceback.print_tb(e.__traceback__)

        gdb.prompt_hook = prompt_until_exit


GDBConsoleWrapper()
