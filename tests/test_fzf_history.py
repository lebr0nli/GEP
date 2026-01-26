from conftest import GDBSession

# TODO: Maybe a better way to handle this?
FZF_POINTER = b"\xe2\x96\x8c"  # ▌


def test_fzf_history_search(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 10", "print 11", "print 20"])

    # search with empty buffer
    gdb_session.send_key("C-r")
    pane_content = gdb_session.capture_pane()
    assert b"3/3" in pane_content
    b"""\
> print 20
  print 11
  print 10""" in pane_content

    # search "11" in buffer
    gdb_session.send_literal("11")
    pane_content = gdb_session.capture_pane()
    assert b"> 11" in pane_content
    assert b"1/3" in pane_content
    assert FZF_POINTER + b" print 11" in pane_content

    # the selected history should be replaced in buffer
    gdb_session.send_key("Enter")
    assert b"(gdb) print 11" == gdb_session.capture_pane()

    # clear the buffer
    gdb_session.send_key("C-u")
    assert b"(gdb)" == gdb_session.capture_pane()

    # search with "print " in buffer
    gdb_session.send_literal("print ")
    original_pane = gdb_session.capture_pane(
        with_color=True
    )  # use color to make sure it is exactly the same
    gdb_session.send_key("C-r")
    assert b"3/3" in gdb_session.capture_pane()

    # put some garbage in buffer
    gdb_session.send_literal("garbage")
    assert b"0/3" in gdb_session.capture_pane()

    # check if we cancel the search, it will restore the buffer
    gdb_session.send_key("C-c")
    assert original_pane == gdb_session.capture_pane(with_color=True)
