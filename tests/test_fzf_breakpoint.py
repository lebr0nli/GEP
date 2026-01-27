from conftest import TEST_PROGRAM
from conftest import Breakpoint
from conftest import Fzf
from conftest import GDBSession
from conftest import MacOSKeys


class TestToggleDeleteFunctionality:
    def test_toggle_no_breakpoints_shows_warning(self, gdb_session: GDBSession) -> None:
        gdb_session.start()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"No breakpoints set" in pane_content

    def test_toggle_disables_enabled_breakpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"disabled" in pane_content

    def test_toggle_enables_disabled_breakpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main", "-ex", "disable 1"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"enabled" in pane_content

    def test_toggle_cancel_preserves_breakpoint_state(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        assert Fzf.POINTER in gdb_session.capture_pane()
        gdb_session.send_key("Escape")
        gdb_session.clear_pane()
        gdb_session.send_literal("info breakpoints")
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"main" in pane_content
        assert b"y" in pane_content

    def test_delete_no_breakpoints_shows_warning(self, gdb_session: GDBSession) -> None:
        gdb_session.start()
        gdb_session.send_key("Escape")
        gdb_session.send_key("x")
        pane_content = gdb_session.capture_pane()
        assert b"No breakpoints set" in pane_content

    def test_delete_removes_breakpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("x")
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"deleted" in pane_content

    def test_delete_verifies_breakpoint_removed_from_gdb(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("x")
        gdb_session.send_key("Enter")
        gdb_session.clear_pane()
        gdb_session.send_literal("info breakpoints")
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"No breakpoints" in pane_content

    def test_delete_cancel_preserves_breakpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("x")
        assert Fzf.POINTER in gdb_session.capture_pane()
        gdb_session.send_key("Escape")
        gdb_session.clear_pane()
        gdb_session.send_literal("info breakpoints")
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"main" in pane_content
        assert b"No breakpoints" not in pane_content

    def test_delete_one_of_multiple_breakpoints(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main", "-ex", "break add"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("x")
        gdb_session.send_literal("add")
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"deleted" in pane_content
        gdb_session.clear_pane()
        gdb_session.send_literal("info breakpoints")
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"main" in pane_content
        assert b"add" not in pane_content

    def test_toggle_with_macos_option_t(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_literal(MacOSKeys.OPT_T)
        pane_content = gdb_session.capture_pane()
        assert Fzf.POINTER in pane_content
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"disabled" in pane_content

    def test_delete_with_macos_option_x(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_literal(MacOSKeys.OPT_X)
        pane_content = gdb_session.capture_pane()
        assert Fzf.POINTER in pane_content
        gdb_session.send_key("Enter")
        pane_content = gdb_session.capture_pane()
        assert b"deleted" in pane_content


class TestFzfVisualization:
    def test_shows_breakpoint_list(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert Fzf.POINTER in pane_content
        assert b"main" in pane_content

    def test_shows_multiple_breakpoints(self, gdb_session: GDBSession) -> None:
        gdb_session.start(
            gdb_args=[
                TEST_PROGRAM,
                "-ex",
                "break main",
                "-ex",
                "break add",
                "-ex",
                "break multiply",
            ]
        )
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"3/3" in pane_content

    def test_can_filter_breakpoints(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main", "-ex", "break add"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        gdb_session.send_literal("add")
        pane_content = gdb_session.capture_pane()
        assert b"1/2" in pane_content

    def test_format_shows_breakpoint_number(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"[1]" in pane_content

    def test_format_enabled_circle_is_red(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane(with_color=True)
        assert Breakpoint.enabled_circle() in pane_content

    def test_format_disabled_circle_is_gray(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main", "-ex", "disable 1"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane(with_color=True)
        assert Breakpoint.disabled_circle() in pane_content

    def test_format_function_breakpoint_location(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break add"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"add" in pane_content

    def test_format_line_breakpoint_location(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break test_program.c:21"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"test_program.c:21" in pane_content

    def test_format_watchpoint_expression(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "watch global_var"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"global_var" in pane_content

    def test_format_read_watchpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "start", "-ex", "rwatch global_var"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"global_var" in pane_content

    def test_format_access_watchpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "start", "-ex", "awatch global_var"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"global_var" in pane_content

    def test_format_catchpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "catch syscall write"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"write" in pane_content or b"syscall" in pane_content

    def test_format_temporary_breakpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "tbreak main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"main" in pane_content

    def test_format_conditional_breakpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break add if a > 5"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"add" in pane_content


class TestPreviewInformation:
    def test_shows_enabled_status(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Enabled" in pane_content

    def test_shows_disabled_status(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main", "-ex", "disable 1"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Disabled" in pane_content

    def test_shows_location(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break add"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Location:" in pane_content

    def test_shows_expression_for_watchpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "watch global_var"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Expression:" in pane_content

    def test_shows_what_for_catchpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "catch syscall write"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"What:" in pane_content

    def test_shows_condition(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break add if a > 5"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Condition:" in pane_content

    def test_shows_hit_count(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Hit count:" in pane_content

    def test_shows_temporary_flag(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "tbreak main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Temporary:" in pane_content

    def test_shows_pending_flag(self, gdb_session: GDBSession) -> None:
        gdb_session.start(
            gdb_args=[
                TEST_PROGRAM,
                "-ex",
                "set breakpoint pending on",
                "-ex",
                "break nonexistent_function",
            ]
        )
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Pending:" in pane_content

    def test_shows_type_for_breakpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "break main"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Type:" in pane_content
        assert b"breakpoint" in pane_content

    def test_shows_type_for_watchpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "watch global_var"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Type:" in pane_content
        assert b"watchpoint" in pane_content

    def test_shows_type_for_catchpoint(self, gdb_session: GDBSession) -> None:
        gdb_session.start(gdb_args=[TEST_PROGRAM, "-ex", "catch syscall write"])
        gdb_session.clear_pane()
        gdb_session.send_key("Escape")
        gdb_session.send_key("t")
        pane_content = gdb_session.capture_pane()
        assert b"Type:" in pane_content
        assert b"catchpoint" in pane_content
