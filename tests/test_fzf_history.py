from conftest import Fzf
from conftest import GDBSession


def test_fzf_history_shows_all_entries(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 10", "print 11", "print 20"])
    gdb_session.send_key("C-r")
    pane_content = gdb_session.capture_pane()
    assert b"3/3" in pane_content
    assert b"print 20" in pane_content
    assert b"print 11" in pane_content
    assert b"print 10" in pane_content


def test_fzf_history_filters_by_query(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 10", "print 11", "print 20"])
    gdb_session.send_key("C-r")
    gdb_session.send_literal("11")
    pane_content = gdb_session.capture_pane()
    assert b"> 11" in pane_content
    assert b"1/3" in pane_content
    assert Fzf.POINTER + b" print 11" in pane_content


def test_fzf_history_select_replaces_buffer(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 10", "print 11", "print 20"])
    gdb_session.send_key("C-r")
    gdb_session.send_literal("11")
    gdb_session.send_key("Enter")
    assert b"(gdb) print 11" == gdb_session.capture_pane()


def test_fzf_history_cancel_restores_buffer(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 10", "print 11", "print 20"])
    gdb_session.send_literal("print ")
    original_pane = gdb_session.capture_pane(with_color=True)
    gdb_session.send_key("C-r")
    assert b"3/3" in gdb_session.capture_pane()
    gdb_session.send_literal("garbage")
    assert b"0/3" in gdb_session.capture_pane()
    gdb_session.send_key("C-c")
    assert original_pane == gdb_session.capture_pane(with_color=True)


def test_fzf_history_navigate_with_tab(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 10", "print 11", "print 20"])
    gdb_session.send_key("C-r")
    gdb_session.send_key("Tab")
    pane_content = gdb_session.capture_pane()
    assert Fzf.POINTER + b" print 11" in pane_content
    gdb_session.send_key("Enter")
    assert b"(gdb) print 11" == gdb_session.capture_pane()


def test_fzf_history_special_characters(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["x/10gx $rsp", "p $rax", "x/4wx $rbp"])
    gdb_session.send_key("C-r")
    gdb_session.send_literal("rsp")
    pane_content = gdb_session.capture_pane()
    assert b"1/3" in pane_content
    gdb_session.send_key("Enter")
    assert b"(gdb) x/10gx $rsp" == gdb_session.capture_pane()


def test_fzf_history_escape_cancels(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 10", "print 11"])
    gdb_session.send_key("C-r")
    assert b"2/2" in gdb_session.capture_pane()
    gdb_session.send_key("Escape")
    assert b"(gdb)" == gdb_session.capture_pane()
