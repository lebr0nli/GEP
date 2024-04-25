from __future__ import annotations

from prompt_toolkit.key_binding import KeyBindings

BINDINGS = KeyBindings()

"""
# You can add your own commands here.
# For example:
DONT_REPEAT = {
    # your functions:
    'foo',
    'bar'
}
"""
DONT_REPEAT: set[str] = set()  # You can modify this line if you want to add your own commands.

"""
# Append your key binding below!
# For example:

from prompt_toolkit.application import run_in_terminal

@BINDINGS.add('c-t')
def _(event):
    " Say 'hello world!' when `c-t` is pressed. "
    def f():
        print('hello world!')
    run_in_terminal(f)

# For more example: https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#adding-custom-key-bindings
"""
