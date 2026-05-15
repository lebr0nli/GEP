import re
from pathlib import Path

from conftest import GDB_HISTORY_NAME
from conftest import GDBSession


def _numbered_command(number: int, command: str) -> bytes:
    return f"{number:5d}  {command}".encode()


def _history_output_lines(pane_content: bytes) -> list[bytes]:
    return [line for line in pane_content.splitlines() if re.match(rb"\s+\d+\s{2}", line)]


def test_show_commands_shows_last_ten_commands(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=[f"print {i}" for i in range(1, 10)])

    gdb_session.send_literal("show commands")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 10
    for i in range(1, 10):
        assert _numbered_command(i, f"print {i}") in pane_content
    assert _numbered_command(10, "show commands") in pane_content


def test_show_commands_shows_less_than_ten_commands(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=[f"print {i}" for i in range(1, 5)])

    gdb_session.send_literal("show commands")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 5
    for i in range(1, 5):
        assert _numbered_command(i, f"print {i}") in pane_content
    assert _numbered_command(5, "show commands") in pane_content


def test_show_commands_shows_ten_commands_with_offset(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=[f"print {i}" for i in range(1, 26)])

    gdb_session.send_literal("show commands 10")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    # Should show 5~14 + show commands (total 10 commands)
    assert len(_history_output_lines(pane_content)) == 10
    for i in range(5, 15):
        assert _numbered_command(i, f"print {i}") in pane_content
    gdb_session.clear_pane()


def test_show_commands_shows_ten_commands_when_offset_near_total(
    gdb_session: GDBSession,
) -> None:
    gdb_session.start(histories=[f"print {i}" for i in range(1, 26)])

    gdb_session.send_literal("show commands 25")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 10
    for i in range(17, 26):
        assert _numbered_command(i, f"print {i}") in pane_content
    assert _numbered_command(26, "show commands 25") in pane_content


def test_show_commands_shows_less_than_ten_commands_with_offset(gdb_session: GDBSession) -> None:
    gdb_session.start(histories=[f"print {i}" for i in range(1, 8)])

    gdb_session.send_literal("show commands 5")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    # Should show 1~7 + show commands (total 8 commands)
    assert len(_history_output_lines(pane_content)) == 8
    for i in range(1, 8):
        assert _numbered_command(i, f"print {i}") in pane_content
    assert _numbered_command(8, "show commands 5") in pane_content


def test_show_commands_plus_continues_after_previous_window(
    gdb_session: GDBSession,
) -> None:
    gdb_session.start(histories=[f"print {i}" for i in range(1, 26)])

    gdb_session.send_literal("show commands 10")
    gdb_session.send_key("Enter")
    gdb_session.clear_pane()

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands +")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 10
    for i in range(15, 25):
        assert _numbered_command(i, f"print {i}") in pane_content
    assert _numbered_command(25, "print 25") not in pane_content
    assert _numbered_command(27, "show commands +") not in pane_content


def test_show_commands_plus_starts_from_beginning_without_previous_window(
    gdb_session: GDBSession,
) -> None:
    gdb_session.start(histories=[f"print {i}" for i in range(1, 26)])

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands +")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 10
    for i in range(1, 11):
        assert _numbered_command(i, f"print {i}") in pane_content
    assert _numbered_command(26, "show commands +") not in pane_content


def test_show_commands_plus_shows_last_window_after_reaching_history_end(
    gdb_session: GDBSession,
) -> None:
    gdb_session.start(histories=[f"print {i}" for i in range(1, 26)])

    gdb_session.send_literal("show commands")
    gdb_session.send_key("Enter")
    gdb_session.clear_pane()

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands +")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 10
    for i in range(18, 26):
        assert _numbered_command(i, f"print {i}") in pane_content
    assert _numbered_command(26, "show commands") in pane_content
    assert _numbered_command(27, "show commands +") in pane_content


def test_show_commands_plus_keeps_last_window_after_repeated_history_end(
    gdb_session: GDBSession,
) -> None:
    gdb_session.start(histories=[f"print {i}" for i in range(1, 26)])

    gdb_session.send_literal("show commands")
    gdb_session.send_key("Enter")
    gdb_session.clear_pane()

    gdb_session.send_literal("show commands +")
    gdb_session.send_key("Enter")
    gdb_session.clear_pane()

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands +")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 10
    for i in range(19, 26):
        assert _numbered_command(i, f"print {i}") in pane_content
    assert _numbered_command(26, "show commands") in pane_content
    assert _numbered_command(27, "show commands +") in pane_content
    assert _numbered_command(28, "show commands +") in pane_content


def test_show_commands_without_remove_duplicates(gdb_session: GDBSession) -> None:
    gdb_session.start(gdb_args=["-ex", "set history remove-duplicates 0"])

    gdb_session.send_literal("print 1")
    gdb_session.send_key("Enter")
    gdb_session.send_literal("print 2")
    gdb_session.send_key("Enter")
    gdb_session.send_literal("print 2")
    gdb_session.send_key("Enter")
    gdb_session.send_literal("print 1")
    gdb_session.send_key("Enter")

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 5
    assert _numbered_command(1, "print 1") in pane_content
    assert _numbered_command(2, "print 2") in pane_content
    assert _numbered_command(3, "print 2") in pane_content
    assert _numbered_command(4, "print 1") in pane_content
    assert _numbered_command(5, "show commands") in pane_content


def test_show_commands_with_remove_duplicates_5(gdb_session: GDBSession) -> None:
    gdb_session.start(gdb_args=["-ex", "set history remove-duplicates 5"])

    for i in range(1, 7):
        gdb_session.send_literal(f"print {i}")
        gdb_session.send_key("Enter")

    # "print 1" should not be removed
    # 1 -> (2 -> 3 -> 4 -> 5 -> 6)
    gdb_session.send_literal("print 1")
    gdb_session.send_key("Enter")

    # "print 3" will be removed and append to the end
    # 1 -> 2 -> (3 -> 4 -> 5 -> 6 -> 1)
    gdb_session.send_literal("print 3")
    gdb_session.send_key("Enter")

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    # After: 1 -> 2 -> 4 -> 5 -> 6 -> 1 -> 3 -> "show commands"
    assert len(_history_output_lines(pane_content)) == 8
    assert _numbered_command(1, "print 1") in pane_content
    assert _numbered_command(2, "print 2") in pane_content
    assert _numbered_command(3, "print 4") in pane_content
    assert _numbered_command(4, "print 5") in pane_content
    assert _numbered_command(5, "print 6") in pane_content
    assert _numbered_command(6, "print 1") in pane_content
    assert _numbered_command(7, "print 3") in pane_content
    assert _numbered_command(8, "show commands") in pane_content


def test_show_commands_with_remove_duplicates_unlimited(gdb_session: GDBSession) -> None:
    gdb_session.start(gdb_args=["-ex", "set history remove-duplicates unlimited"])

    gdb_session.send_literal("print 1")
    gdb_session.send_key("Enter")
    gdb_session.send_literal("print 2")
    gdb_session.send_key("Enter")
    gdb_session.send_literal("print 1")
    gdb_session.send_key("Enter")

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 3
    assert _numbered_command(1, "print 2") in pane_content
    assert _numbered_command(2, "print 1") in pane_content
    assert _numbered_command(3, "show commands") in pane_content


def test_history_save_on() -> None:
    gdb_session = GDBSession()
    gdb_session.start(
        gdb_args=["-ex", "set history save on"], histories=[f"print {i}" for i in range(1, 4)]
    )
    gdb_session.send_literal("print 4")
    gdb_session.send_key("Enter")

    gdb_session.stop()
    new_history = (Path(gdb_session.tmpdir.name) / GDB_HISTORY_NAME).read_text().splitlines()
    gdb_session.exit()

    # History should be updated
    assert len(new_history) == 4
    assert new_history[0] == "print 1"
    assert new_history[1] == "print 2"
    assert new_history[2] == "print 3"
    assert new_history[3] == "print 4"


def test_history_save_off() -> None:
    gdb_session = GDBSession()
    gdb_session.start(
        gdb_args=["-ex", "set history save off"], histories=[f"print {i}" for i in range(1, 4)]
    )
    gdb_session.send_literal("print 4")
    gdb_session.send_key("Enter")

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 5
    for i in range(1, 5):
        assert _numbered_command(i, f"print {i}") in pane_content
    assert _numbered_command(5, "show commands") in pane_content

    gdb_session.stop()
    new_history = (Path(gdb_session.tmpdir.name) / GDB_HISTORY_NAME).read_text().splitlines()
    gdb_session.exit()

    # History should not be updated
    assert len(new_history) == 3
    assert new_history[0] == "print 1"
    assert new_history[1] == "print 2"
    assert new_history[2] == "print 3"


def test_truncation_of_loaded_history(gdb_session: GDBSession) -> None:
    history_size = 256
    gdb_session.start(
        gdb_args=["-ex", f"set history size {history_size}"],
        histories=[f"print {i}" for i in range(1, history_size + 1)],
    )

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands 1")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 10
    for i in range(2, 12):
        assert _numbered_command(i, f"print {i}") in pane_content

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands 1")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    assert len(_history_output_lines(pane_content)) == 10
    for i in range(3, 13):
        assert _numbered_command(i, f"print {i}") in pane_content

    gdb_session.clear_pane()
    gdb_session.send_literal("show commands")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()

    current_max = history_size + 3
    assert len(_history_output_lines(pane_content)) == 10
    for i in range(current_max, current_max - 10, -1):
        if i == current_max:
            assert _numbered_command(i, "show commands") in pane_content
        elif i == current_max - 1 or i == current_max - 2:
            assert _numbered_command(i, "show commands 1") in pane_content
        else:
            assert _numbered_command(i, f"print {i}") in pane_content
