from conftest import Ansi
from conftest import GDBSession


def test_autosuggestion_no_match(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 12", "print 34"])
    gdb_session.send_literal("print x")
    assert b"(gdb) print x" == gdb_session.capture_pane(with_color=True)


def test_autosuggestion_shows_most_recent_match(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 12", "print 34"])
    gdb_session.send_literal("print ")
    assert b"(gdb) print " + Ansi.suggestion(b"34") == gdb_session.capture_pane(with_color=True)


def test_autosuggestion_accept_with_right_arrow(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 12", "print 34"])
    gdb_session.send_literal("print ")
    gdb_session.send_key("Right")
    assert b"(gdb) print 34" == gdb_session.capture_pane(with_color=True)


def test_autosuggestion_updates_as_typing(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 12", "print 34"])
    gdb_session.send_literal("print 1")
    assert b"(gdb) print 1" + Ansi.suggestion(b"2") == gdb_session.capture_pane(with_color=True)
    gdb_session.send_key("Right")
    assert b"(gdb) print 12" == gdb_session.capture_pane(with_color=True)


def test_autosuggestion_empty_history(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=[])
    gdb_session.send_literal("print 1")
    assert b"(gdb) print 1" == gdb_session.capture_pane(with_color=True)
