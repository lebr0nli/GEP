import os
import re
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
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.output import create_output
from prompt_toolkit.shortcuts import CompleteStyle

# global variables
HAS_FZF = which("fzf") is not None
HISTORY_FILENAME = ".gdb_history"
# This sucks, but there's not a GDB API for checking dont-repeat now.
# I just collect some common used commands which should not be repeated.
# If you have some user-define function, add your command into the list manually.
# If you found a command should/shouldn't in this list, please let me know on the issue page, thanks!
DONT_REPEAT = {
    # original GDB
    "attach",
    "run",
    "r",
    "detach",
    "help",
    "complete",
    "quit",
    "q",
    # for GEF
    "theme",
    "canary",
    "functions",
    "gef",
    "tmux-setup",
}

try:
    from geprc import BINDINGS
    from geprc import DONT_REPEAT as USER_DONT_REPEAT

    DONT_REPEAT = DONT_REPEAT.union(USER_DONT_REPEAT)
except ImportError:
    from prompt_toolkit.key_binding import KeyBindings

    BINDINGS = KeyBindings()


# function for logging
def print_info(s):
    print_formatted_text(FormattedText([("#00FFFF", s)]), file=sys.__stdout__)


def print_warning(s):
    print_formatted_text(FormattedText([("#FFCC00", s)]), file=sys.__stdout__)


class UserParamater(gdb.Parameter):
    gep_loaded = False

    def __init__(
        self,
        name,
        default_value,
        set_show_doc,
        parameter_class,
        help_doc="",
        enum_sequence=None,
    ):
        self.set_show_doc = set_show_doc
        self.set_doc = "Set %s." % self.set_show_doc
        self.show_doc = "Show %s." % self.set_show_doc
        self.__doc__ = help_doc.strip() or None
        if enum_sequence:
            super().__init__(name, gdb.COMMAND_NONE, parameter_class, enum_sequence)
        else:
            super().__init__(name, gdb.COMMAND_NONE, parameter_class)
        self.value = default_value

    def get_set_string(self):
        if not self.gep_loaded:
            return ""
        svalue = self.value
        # TODO: Support other type when needed
        if isinstance(svalue, bool):
            svalue = "on" if svalue else "off"
        return "Set %s to %r." % (self.set_show_doc, svalue)

    def get_show_string(self, svalue):
        if not self.gep_loaded:
            return ""
        return "%s is %r." % (self.set_show_doc.capitalize(), svalue)


ctrl_c_quit = UserParamater(
    "ctrl-c-quit", False, "whether to use ctrl-c to exit the gdb", gdb.PARAM_BOOLEAN
)

single_column_tab_complete = UserParamater(
    "single-column-tab-complete",
    True,
    "whether to use single column for tab completion",
    gdb.PARAM_BOOLEAN,
)

# key binding for fzf history search
if HAS_FZF:

    @BINDINGS.add("c-r")
    def _(event: KeyPressEvent):
        """Reverse search history with fzf."""

        def f():
            global HISTORY_FILENAME
            if not os.path.exists(HISTORY_FILENAME):
                # just create an empty file
                with open(HISTORY_FILENAME, "w"):
                    pass
            fzf_cmd = (
                "fzf",
                "--tiebreak=index",
                "--no-multi",
                "--height=40%",
                "--layout=reverse",
                "--query",
            )
            fzf_cmd += (event.app.current_buffer.document.text_before_cursor,)
            p = Popen(fzf_cmd, stdin=PIPE, stdout=PIPE, text=True)
            with open(HISTORY_FILENAME) as f:
                visited = set()
                # Reverse the history, and only keep the youngest and unique one
                for line in f.read().strip().split("\n")[::-1]:
                    if line and not line in visited:
                        visited.add(line)
                        p.stdin.write(line + "\n")
            stdout, _ = p.communicate()
            if stdout:
                event.app.current_buffer.document = Document()  # clear buffer
                event.app.current_buffer.insert_text(stdout.strip())

        run_in_terminal(f)

else:
    print_warning("Install fzf for better experience with GEP")


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
            with open(self.filename, "rb") as f:
                for line in f:
                    line = line.decode("utf-8")
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
        with open(self.filename, "ab") as f:
            f.write(string.strip().encode() + b"\n")


class GDBCompleter(Completer):
    """
    Completer of GDB
    """

    def __init__(self):
        super().__init__()

    def get_completions(self, document, complete_event):
        completions_limit = gdb.parameter("max-completions")
        if completions_limit == -1:
            completions_limit = 0xFFFFFFFF
        if completions_limit == 0:
            return
        if (
            document.text_before_cursor.strip()
            and document.text_before_cursor[-1].isspace()
        ):
            # fuzzing all possible commands if the text before cursor endswith space
            all_completions = []
            for c in ascii_letters + "_-":
                if completions_limit <= 0:
                    break
                completions = gdb.execute(
                    "complete %s" % document.text_before_cursor + c, to_string=True
                ).split("\n")
                completions.pop()  # remove empty line
                if (
                    completions
                    and " *** List may be truncated, max-completions reached. ***"
                    == completions[-1]
                ):
                    completions.pop()
                all_completions = chain(
                    all_completions, completions[:completions_limit]
                )
                completions_limit -= len(completions)
        else:
            all_completions = gdb.execute(
                "complete %s" % document.text_before_cursor, to_string=True
            ).split("\n")
            all_completions.pop()  # remove empty line
            if (
                all_completions
                and " *** List may be truncated, max-completions reached. ***"
                == all_completions[-1]
            ):
                all_completions.pop()

        should_display_docstring = True
        for completion in all_completions:
            display_meta = None
            try:
                if (
                    " " not in completion
                    or re.match(r"^show\s", completion)
                    or re.match(r"^info\s+set\s", completion)
                    or re.match(r"^inf\s+set\s", completion)
                    or re.match(r"^i\s+set\s", completion)
                ):
                    # raw completion may be a command, try to show its docstring
                    # also, `show <param>` is also a command, we try to show its docstring
                    # Note: `info set <param>` is a alias of `show <param>`
                    display_meta = (
                        gdb.execute("help %s" % completion, to_string=True).strip()
                        or None
                    )
                elif should_display_docstring:
                    if (
                        re.match(r"^set\s", completion)
                        or re.match(r"^info\s", completion)
                        or re.match(r"^inf\s", completion)
                        or re.match(r"^i\s", completion)
                    ):
                        # `set <param-name>`, `info <param-name>` is also a command, we try to show its docstring
                        display_meta = (
                            gdb.execute("help %s" % completion, to_string=True).strip()
                            or None
                        )
                        if display_meta and len(completion.split()) > 2:
                            # when completion == `set foo bar`
                            # check `set foo bar` is a subcommand of `set foo` or not, if not, `bar` is a value, we shouldn't show the docstring for it
                            # but, there is no a good API to check it, so we just check the docstring contains keyword:
                            # `Type "help set foo" followed by set foo subcommand name for full documentation.`
                            # Note: `info` have the same problem
                            normalize_command = completion.split()[:-1]
                            if normalize_command[0] in ("inf", "i"):
                                normalize_command[0] = "info"
                            parent_command = " ".join(normalize_command)

                            keyword = (
                                'Type "help %s" followed by %s subcommand name for full documentation.'
                                % (
                                    parent_command,
                                    parent_command,
                                )
                            )
                            parent_command_docstring = gdb.execute(
                                "help %s" % parent_command, to_string=True
                            )
                            if keyword not in parent_command_docstring:
                                display_meta = None
                                # We don't need to do this check again, because all other completions have the same prefix
                                should_display_docstring = False
            except gdb.error:
                # this is not a command
                pass
            # remove some prefix of raw completion
            completion = completion.replace(document.text_before_cursor.lstrip(), "")
            # display readable completion based on the text before cursor
            display = re.split(r"\W+", document.text_before_cursor)[-1] + completion
            yield Completion(completion, display=display, display_meta=display_meta)


class GDBConsoleWrapper:
    """
    Wrapper of original GDB console
    """

    def __init__(self):
        old_prompt_hook = gdb.prompt_hook

        def prompt_until_exit(current_prompt):
            gdb.prompt_hook = old_prompt_hook  # retrieve old prompt hook
            print_info("GEP is running now!")
            UserParamater.gep_loaded = True
            history_on = gdb.parameter("history save")
            if history_on:
                global HISTORY_FILENAME
                HISTORY_FILENAME = gdb.parameter("history filename")
                is_ignore_duplicates = -1 == gdb.parameter("history remove-duplicates")
                gdb_history = GDBHistory(
                    HISTORY_FILENAME, ignore_duplicates=is_ignore_duplicates
                )
            else:
                print_warning("`set history save on` for better experience with GEP")
                gdb_history = InMemoryHistory()
            session = PromptSession(
                history=gdb_history,
                enable_history_search=True,
                auto_suggest=AutoSuggestFromHistory(),
                completer=GDBCompleter(),
                complete_style=CompleteStyle.COLUMN
                if single_column_tab_complete.value
                else CompleteStyle.MULTI_COLUMN,
                complete_while_typing=False,
                key_bindings=BINDINGS,
                output=create_output(stdout=sys.__stdout__),
            )
            while True:
                try:
                    # emulate the original prompt
                    prompt_string = (
                        gdb.prompt_hook(current_prompt) if gdb.prompt_hook else None
                    )
                    if prompt_string is None:  # prompt string is set by gdb command
                        prompt_string = gdb.parameter("prompt")
                    prompt_string = prompt_string.replace("\001", "").replace(
                        "\002", ""
                    )  # fix for ANSI prompt
                    gdb_cmd = session.prompt(ANSI(prompt_string))
                    if not gdb_cmd.strip():
                        gdb_cmd_list = gdb_history.get_strings()
                        if gdb_cmd_list:
                            previous_gdb_cmd = gdb_cmd_list[-1]
                            if (
                                previous_gdb_cmd.split()
                                and previous_gdb_cmd.split()[0] not in DONT_REPEAT
                            ):
                                gdb_cmd = previous_gdb_cmd
                    gdb.execute(gdb_cmd, from_tty=True)
                except gdb.error as e:
                    print(e)
                except KeyboardInterrupt:
                    if ctrl_c_quit.value:
                        gdb.execute("quit")
                except EOFError:
                    gdb.execute("quit")
                except Exception as e:
                    print(e)
                    traceback.print_tb(e.__traceback__)

        gdb.prompt_hook = prompt_until_exit


GDBConsoleWrapper()


class UpdateGEPCommand(gdb.Command):
    """
    Update GEP to the latest version
    """

    def __init__(self):
        super(UpdateGEPCommand, self).__init__("gep-update", gdb.COMMAND_NONE)

    def invoke(self, arg, from_tty):
        print_info("Updating GEP...")
        gep_filename = os.path.expanduser("~/GEP/.gdbinit-gep.py")
        if not os.path.exists(gep_filename):
            print_warning("GEP is not installed at %s, update aborted" % gep_filename)
            return
        with open(gep_filename, "r") as f:
            try:
                import urllib.request

                content = f.read()
                remote_content = urllib.request.urlopen(
                    "https://raw.githubusercontent.com/lebr0nli/GEP/main/gdbinit-gep.py"
                ).read()
            except Exception as e:
                print(e)
                print_warning("Failed to download GEP from Github")
                return
            if content == remote_content.decode("utf-8"):
                print_info("GEP is already the latest version.")
                return
        with open(gep_filename, "w") as f:
            f.write(remote_content.decode("utf-8"))
        print_info("GEP is updated to the latest version.")


UpdateGEPCommand()
