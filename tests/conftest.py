from __future__ import annotations

import functools
import os
import subprocess
import tempfile
import time
import typing as T

import pytest

SESSION_STARTUP_TIMEOUT = 15
STARTUP_BANNER = b"GEP is running now!"
GDB_HISTORY_NAME = ".gdb_history"


def run_with_screen_256color(
    cmd: list[str], capture_output: bool = False
) -> subprocess.CompletedProcess:
    """
    Run a command with `TERM=screen-256color`.

    :param list[str] cmd: The command to run.
    :param bool capture_output: Whether to capture the output.
    :return: The result of the command.
    :rtype: subprocess.CompletedProcess
    """
    env = os.environ.copy()
    env["TERM"] = "screen-256color"
    return subprocess.run(cmd, capture_output=capture_output, env=env)


class GDBSession:
    def __init__(self) -> None:
        """
        Initialize the GDB session.
        """
        self.tmpdir = tempfile.TemporaryDirectory()

        self.session_name = None
        self.__session_started = False

    def start(self, gdb_args: list[str] | None = None, histories: list[str] = None) -> None:
        """
        Start the GDB session.

        :param list[str] gdb_args: The arguments to pass to GDB.
        :param list[str] histories: The histories to load into GDB.
        :return: None
        """
        if histories:
            with open(os.path.join(self.tmpdir.name, GDB_HISTORY_NAME), "w") as f:
                f.write("\n".join(histories))

        cmd = [
            "tmux",
            "new-session",
            "-f",
            os.devnull,
            "-d",
            "-P",
            "-F",
            "#{session_name}",
            "-c",
            self.tmpdir.name,
            "gdb",
            "-q",
        ]
        if gdb_args:
            cmd.extend(gdb_args)

        self.session_name = (
            run_with_screen_256color(cmd, capture_output=True).stdout.decode().strip()
        )
        self.__session_started = True

        # wait `STARTUP_BANNER` appears in pane
        now = time.time()
        while time.time() - now < SESSION_STARTUP_TIMEOUT:
            if STARTUP_BANNER in self.capture_pane():
                break
            time.sleep(1)
        else:
            raise TimeoutError("GDB session did not start in time")
        self.clear_pane()

    def stop(self) -> None:
        """
        Remove the temporary directory and stop the GDB session.

        :return: None
        """
        self.tmpdir.cleanup()
        if self.__session_started:
            run_with_screen_256color(["tmux", "kill-session", "-t", self.session_name])
            self.__session_started = False

    def check_session_started(func: T.Callable) -> T.Callable:
        """
        Check if the GDB session is started before calling the decorated function.

        :param Callable func: The function to decorate.
        :return: The decorated function.
        :rtype: Callable
        :raises RuntimeError: If the GDB session is not started.
        """

        @functools.wraps(func)
        def wrapper(self: GDBSession, *args, **kwargs):
            if not self.__session_started:
                raise RuntimeError("GDB session is not started")
            return func(self, *args, **kwargs)

        return wrapper

    @check_session_started
    def send_literal(self, literal: str) -> None:
        """
        Send a literal string to the GDB session.

        :param str literal: The literal string to send to the GDB session.
        :return: None
        """
        run_with_screen_256color(["tmux", "send-keys", "-l", "-t", self.session_name, literal])
        time.sleep(1)

    @check_session_started
    def send_key(self, key: str) -> None:
        """
        Send a key to the GDB session.

        :param str key: The key to send to the GDB session.
        :return: None
        """
        run_with_screen_256color(["tmux", "send-keys", "-t", self.session_name, key])
        time.sleep(1)

    @check_session_started
    def clear_pane(self) -> None:
        """
        Clear the screen of the pane.

        :return: None
        :rtype: None
        """
        run_with_screen_256color(["tmux", "send-keys", "-t", self.session_name, "C-l"])
        time.sleep(1)
        run_with_screen_256color(["tmux", "clear-history", "-t", self.session_name])

    @check_session_started
    def capture_pane(self, with_color: bool = False) -> bytes:
        """
        Capture the content of the pane.

        :param bool with_color: Whether to capture the content with color.
        :return: The content of the pane.
        :rtype: bytes
        """
        cmd = ["tmux", "capture-pane", "-p", "-t", self.session_name]
        if with_color:
            cmd.append("-e")
        return run_with_screen_256color(cmd, capture_output=True).stdout.rstrip(b"\n")

    def __enter__(self) -> GDBSession:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()


@pytest.fixture
def gdb_session() -> T.Iterator[GDBSession]:
    with GDBSession() as session:
        yield session
