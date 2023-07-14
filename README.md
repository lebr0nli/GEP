# GEP (GDB Enhanced Prompt)

[![asciicast](https://asciinema.org/a/TJiEkHv3cqieR0XizG41uOg93.svg)](https://asciinema.org/a/TJiEkHv3cqieR0XizG41uOg93)

`GEP` (GDB Enhanced Prompt) is a GDB plug-in which make your GDB command prompt more convenient and flexibility.

## Why I need this plug-in?

GDB's original prompt is using hardcoded built-in GNU readline library, we can't add our custom function and key binding
easily. The old way to implement them is by patching the GDB's C source code and compiling it again.

But now, you can write your function in Python and use arbitrary key binding easily with GEP without any patching!

And also, GEP has some awesome features already, you can directly use it!

## Features

- <kbd>Ctrl</kbd>+<kbd>r</kbd> for [fzf](https://github.com/junegunn/fzf) history reverse search
- <kbd>↑</kbd> key for partial string matching in history
- <kbd>TAB</kbd> for auto-completion with:
  - fzf (When fzf is installed)
  - floating window (Similar to IPython's auto-completion)
- [fish](https://fishshell.com)-like autosuggestions (<kbd>→</kbd> key to accept the suggestion)
- has the ability to build custom key binding and its callback function by modifying `geprc.py`

## How to install it?

Make sure you have GDB 8.0 or higher compiled with Python3.7+ bindings, then:

1. Install fzf: [Installation](https://github.com/junegunn/fzf#installation)

2. Install this plug-in by:

```shell
# via the install script
## using curl
$ bash -c "$(curl -fsSL https://raw.githubusercontent.com/lebr0nli/GEP/main/install.sh)"

## using wget
$ bash -c "$(wget https://raw.githubusercontent.com/lebr0nli/GEP/main/install.sh -O -)"

# manually
$ pip install --no-cache-dir prompt_toolkit
$ git clone https://github.com/lebr0nli/GEP.git ~/.local/share/GEP
$ printf '\nsource ~/.local/share/GEP/gdbinit-gep.py\n' >> ~/.gdbinit
```

3. Enjoy!

## How to update the version of GEP?

In your GDB, use `gep-update` command, or you can manually use `wget` or `curl` to download the [gdbinit-gep.py](./gdbinit-gep.py) again.

```shell
# e.g. using wget and your GEP is installed in ~/.local/share/GEP
wget https://raw.githubusercontent.com/lebr0nli/GEP/main/gdbinit-gep.py -O ~/.local/share/GEP/gdbinit-gep.py
```

## For more configuration

You can modify the configuration for history, auto-completion, and other GEP configurations in `/path/to/GEP/gdbinit-gep`.

You can also add your custom key bindings by modifying `/path/to/GEP/geprc.py`.

## The trade-offs

Since GDB doesn't have a good Python API to fully control and emulate its prompt, this plug-in has some side
effects.

However, the side effects are avoidable, here are the guides to avoid them:

### `TUI mode`

Somehow, GEP breaks the TUI mode in GDB, so it's advisable not to use GDB's built-in TUI when working with GEP (refer to issue #13).

Alternatively, I personally recommend trying [pwndbg/pwndbg](https://github.com/pwndbg/pwndbg) or [hugsy/gef](https://github.com/hugsy/gef) for their user-friendly features.

> If you have any ideas to resolve this issue, PRs are greatly appreciated. 🙏

### `gdb.event.before_prompt`

The GDB Python API event: `gdb.event.before_prompt` may be called only once.

So if you are using a GDB plug-in that is listening on this event, this plug-in will cause some bugs.

> **Note**
> As far as I know, pwndbg and gef won't be bothered by this side effect now.

To avoid this, you can change the callback function by adding them to `gdb.prompt_hook`, `gdb.prompt_hook` has almost
the same effects with `event.before_prompt`, but `gdb.prompt_hook` can be directed invoke, so this plug-in still can
emulate that callback for you!

### `dont-repeat`

When your input is empty and directly press <kbd>ENTER</kbd>, GDB will execute the previous command from history if that command
doesn't have the property: `dont-repeat`.

As far as I know, there is no GDB API for checking a command's property.

So, I added some commonly used commands (for original GDB API and GEF) which have that property in a set to avoid
repeatedly executing them.

If you have some user-defined function that has `dont-repeat` property, add your command into the set manually, too.

> **Note**
> The set of those user-defined commands are in `geprc.py` and the variable name for it is `DONT_REPEAT`.
>
> If you found some builtin commands which should or shouldn't be added by default, let me know on the issue page, thanks!

## Credits

Some ideas/code are inspired by [hugsy/gef](https://github.com/hugsy/gef) and [pwndbg/pwndbg](https://github.com/pwndbg/pwndbg).

Thanks!

## Bugs, suggestions, and ideas

If you found any bug, or you have any suggestions/ideas about this plug-in, feel free to leave your feedback on the
GitHub issue page or send me a pull request!

Thanks!
