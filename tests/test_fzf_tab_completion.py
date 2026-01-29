from pathlib import Path

from conftest import TEST_PROGRAM_C
from conftest import TEST_PROGRAM_CPP
from conftest import Fzf
from conftest import GDBSession


def test_fzf_tab_shows_completions(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("b")
    gdb_session.send_key("Tab")
    pane_content = gdb_session.capture_pane()
    assert Fzf.POINTER in pane_content
    assert b"break" in pane_content


def test_fzf_tab_filters_completions(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("b")
    gdb_session.send_key("Tab")
    pane_content = gdb_session.capture_pane()
    assert b"break" in pane_content
    assert b"backtrace" in pane_content


def test_fzf_tab_select_replaces_buffer(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("info ")
    gdb_session.send_key("Tab")
    gdb_session.send_literal("breakp")
    gdb_session.send_key("Enter")
    assert b"(gdb) info breakpoints" == gdb_session.capture_pane()


def test_fzf_tab_cancel_restores_buffer(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("b")
    original_pane = gdb_session.capture_pane(with_color=True)
    gdb_session.send_key("Tab")
    assert Fzf.POINTER in gdb_session.capture_pane()
    gdb_session.send_key("C-c")
    assert original_pane == gdb_session.capture_pane(with_color=True)


def test_fzf_tab_navigate_with_tab(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("info ")
    gdb_session.send_key("Tab")
    first_pane = gdb_session.capture_pane()
    gdb_session.send_key("Tab")
    second_pane = gdb_session.capture_pane()
    assert first_pane != second_pane


def test_fzf_tab_escape_cancels(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("b")
    gdb_session.send_key("Tab")
    assert Fzf.POINTER in gdb_session.capture_pane()
    gdb_session.send_key("Escape")
    assert b"(gdb) b" == gdb_session.capture_pane()


def test_fzf_tab_no_completions_no_fzf(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("nonexistentcommandxyz")
    gdb_session.send_key("Tab")
    pane_content = gdb_session.capture_pane()
    assert Fzf.POINTER not in pane_content
    assert b"(gdb) nonexistentcommandxyz" == pane_content


def test_fzf_tab_subcommand_completion(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("info ")
    gdb_session.send_key("Tab")
    gdb_session.send_literal("breakp")
    gdb_session.send_key("Enter")
    assert b"(gdb) info breakpoints" == gdb_session.capture_pane()


def test_fzf_tab_set_command_completion(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("set pa")
    gdb_session.send_key("Tab")
    pane_content = gdb_session.capture_pane()
    assert b"pagination" in pane_content


def test_fzf_tab_after_whitespace(gdb_session: GDBSession) -> None:
    gdb_session.start()
    gdb_session.send_literal("  info ")
    gdb_session.send_key("Tab")
    gdb_session.send_literal("breakp")
    gdb_session.send_key("Enter")
    assert b"(gdb)   info breakpoints" == gdb_session.capture_pane()


def test_fzf_tab_navigate_with_shift_tab(gdb_session: GDBSession) -> None:
    """Test that Shift-Tab navigates up in fzf."""
    gdb_session.start()
    gdb_session.send_literal("info ")
    gdb_session.send_key("Tab")
    first_pane = gdb_session.capture_pane()
    gdb_session.send_key("Tab")
    second_pane = gdb_session.capture_pane()
    gdb_session.send_key("BTab")
    third_pane = gdb_session.capture_pane()
    assert first_pane != second_pane
    assert first_pane == third_pane


def test_fzf_tab_single_match_auto_selects(gdb_session: GDBSession) -> None:
    """Test that a single match is automatically selected (--select-1)."""
    gdb_session.start()
    gdb_session.send_literal("info warran")
    gdb_session.send_key("Tab")
    assert b"(gdb) info warranty" == gdb_session.capture_pane()


def test_fzf_tab_cpp_completion_preserves_prefix(gdb_session: GDBSession) -> None:
    """
    Test that C++ completion preserves the correct prefix (issue #14, PR #15 fix).

    This tests the bug where 'b B<tab>' would show 'Boo::B::func()' instead of
    'foo::B::func()' - the first character was incorrectly replaced.
    We want to ensure the correct prefix is preserved.
    """
    gdb_session.start(gdb_args=[TEST_PROGRAM_CPP])
    gdb_session.send_literal("b test")
    gdb_session.send_key("Tab")
    pane_content = gdb_session.capture_pane()

    # Make sure both the filename and function appear in the completions:
    # (gdb) complete b test
    # b foo::B::testing()
    # b test_program_cpp.cc
    assert Fzf.POINTER in pane_content
    assert b"foo::B::testing()" in pane_content
    assert Path(TEST_PROGRAM_CPP).name.encode() in pane_content

    # Our program should be able to complete to foo::B::testing() correctly
    gdb_session.send_literal("foo::")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()
    assert b"(gdb) b foo::B::testing()" == pane_content


def test_fzf_tab_quoted_symbol_completion(gdb_session: GDBSession) -> None:
    """
    Test completion of quoted symbols includes closing quote (PR #15 fix).

    This tests the bug handling quoted symbols for commands like 'b' and 'p'.
    """
    gdb_session.start(gdb_args=[TEST_PROGRAM_C])
    gdb_session.send_literal("b 'm")
    gdb_session.send_key("Tab")
    gdb_session.send_literal("ain")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()
    assert b"(gdb) b 'main'" == pane_content

    # Clean up for next interaction
    gdb_session.send_key("C-c")
    gdb_session.clear_pane()

    gdb_session.send_literal("p 'm")
    gdb_session.send_key("Tab")
    gdb_session.send_literal("ain")
    gdb_session.send_key("Enter")
    pane_content = gdb_session.capture_pane()
    assert b"(gdb) p 'main'" == pane_content


def test_preview_shows_help_documentation(gdb_session: GDBSession) -> None:
    """Test that preview panel shows GDB help documentation for commands."""
    gdb_session.start()
    gdb_session.send_literal("b")
    gdb_session.send_key("Tab")
    pane_content = gdb_session.capture_pane()
    assert Fzf.POINTER in pane_content
    assert b"backtrace, where, bt" in pane_content
    assert b"Print backtrace" in pane_content

    gdb_session.send_literal("reak")
    pane_content = gdb_session.capture_pane()
    assert b"break, brea, bre, br, b" in pane_content
    assert b"Set breakpoint" in pane_content
