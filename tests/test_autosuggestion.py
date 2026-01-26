from conftest import GDBSession


def grey(b: bytes) -> bytes:
    """
    Return the grey version of the bytes.

    :param bytes b: The bytes to make grey.
    :return: The grey version of the bytes.
    :rtype: bytes
    """
    return b"\x1b[38;5;241m" + b + b"\x1b[39m"


def test_autosuggestion(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=["print 12", "print 34"])

    # the autosuggestion should not be shown when no match
    gdb_session.send_literal("print x")
    assert b"(gdb) print x" == gdb_session.capture_pane(with_color=True)

    # make buffer to "print "
    gdb_session.send_key("BSpace")
    gdb_session.send_key("BSpace")
    gdb_session.send_literal(" ")
    # match "print 34"
    assert b"(gdb) print " + grey(b"34") == gdb_session.capture_pane(with_color=True)
    # accept the suggestion
    gdb_session.send_key("Right")
    assert b"(gdb) print 34" == gdb_session.capture_pane(with_color=True)

    # make buffer to "print 1"
    gdb_session.send_key("BSpace")
    gdb_session.send_key("BSpace")
    gdb_session.send_literal("1")
    # match "print 2"
    assert b"(gdb) print 1" + grey(b"2") == gdb_session.capture_pane(with_color=True)
    # accept the suggestion
    gdb_session.send_key("Right")
    assert b"(gdb) print 12" == gdb_session.capture_pane(with_color=True)
