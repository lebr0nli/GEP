import gdb
import ast
import os
import traceback
import shlex
import sys
from shutil import which
from subprocess import Popen, PIPE

# setup import path
directory, file = os.path.split(__file__)
directory = os.path.expanduser(directory)
directory = os.path.abspath(directory)
sys.path.append(directory)

# import prompt_toolkit 2.0.10 for GEP
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.application import run_in_terminal

# global variables
HAS_FZF = which('fzf') is not None
HISTORY_FILENAME = '.gdb_history'
from geprc import BINDINGS


# function for logging
def print_info(s):
    print_formatted_text(FormattedText([('#00FFFF', s)]))


def print_warning(s):
    print_formatted_text(FormattedText([('#FFCC00', s)]))


# key binding for fzf history search
if HAS_FZF:
    @BINDINGS.add('c-r')
    def _(event):
        """ Reverse search history with fzf. """

        def f():
            query = shlex.quote(event.app.current_buffer.text)
            global HISTORY_FILENAME
            if not os.path.exists(HISTORY_FILENAME):
                # just create an empty file
                with open(HISTORY_FILENAME, 'w'):
                    pass
            fzf_cmd = [f"awk '!seen[$0]++' {HISTORY_FILENAME}"]
            fzf_cmd += [f"fzf --tiebreak=index --no-multi --height=40% --layout=reverse --tac --query={query}"]
            fzf_cmd = '|'.join(fzf_cmd)
            p = Popen(fzf_cmd, shell=True, stdout=PIPE, text=True)
            stdout, _ = p.communicate()
            event.app.current_buffer.delete_before_cursor(len(event.app.current_buffer.text))
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
        super(GDBHistory, self).__init__(filename=filename)

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
        super(Completer, self).__init__()

    def get_completions(self, document, complete_event):
        all_completions = gdb.execute(f'complete {document.text}', to_string=True).split('\n')
        all_completions.pop()  # remove empty line
        if all_completions and 'max-completions reached' in all_completions[-1]:
            all_completions.pop()
        for completion in all_completions:
            yield Completion(completion.replace(document.text.strip(), ''), display=completion.split()[-1])


class GDBConsoleWrapper:
    """
    Wrapper of original GDB console
    """

    def __init__(self):
        old_prompt_hook = gdb.prompt_hook

        def prompt_until_exit(current_prompt):
            print_info('GEP is running now!')
            history_on = 'off' not in gdb.execute('show history save', to_string=True)
            if history_on:
                global HISTORY_FILENAME
                HISTORY_FILENAME = gdb.execute('show history filename', to_string=True)[55:-2]
                HISTORY_FILENAME = ast.literal_eval(HISTORY_FILENAME)  # parse escape character
                is_ignore_duplicates = "unlimited" in gdb.execute('show history remove-duplicates', to_string=True)
                session = PromptSession(
                    history=GDBHistory(HISTORY_FILENAME, ignore_duplicates=is_ignore_duplicates),
                    enable_history_search=True,
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=GDBCompleter(),
                    complete_while_typing=False,
                    key_bindings=BINDINGS
                )
            else:
                print_warning('`set history save on` for better experience with GEP')
                session = PromptSession(
                    history=InMemoryHistory(),
                    enable_history_search=True,
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=GDBCompleter(),
                    complete_while_typing=False,
                    key_bindings=BINDINGS
                )
            while True:
                # emulate the original prompt
                prompt_string = old_prompt_hook(current_prompt) if old_prompt_hook else None
                if prompt_string is None:  # prompt string is set by gdb command
                    prompt_string = gdb.execute('show prompt', to_string=True)[16:-2]
                    prompt_string = prompt_string.replace('\\e', '\033')  # fix for color string
                    prompt_string = ast.literal_eval(prompt_string)  # parse escape character
                prompt_string = prompt_string.replace('\001', '').replace('\002', '')  # fix for ANSI prompt
                try:
                    gdb_cmd = session.prompt(ANSI(prompt_string))
                    try:
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
