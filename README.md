# GEP (GDB Enhanced Prompt)

[![asciicast](https://asciinema.org/a/TJiEkHv3cqieR0XizG41uOg93.svg)](https://asciinema.org/a/TJiEkHv3cqieR0XizG41uOg93)

`GEP` (GDB Enhanced Prompt) is a GDB plug-in which make your GDB console's prompt more convinent and flexibility.

## Why I need this plug-in?

GDB's original prompt is using hardcoded built-in GNU readline library, we can't add our custom function and key binding easily. The old way to implement them is by patching the GDB's C source code and compiling it again.

Now, you can write your function in Python and use arbitrary key binding easily with GEP!

And also, GEP has some awesome features already, you can directly use it!

## Features

- `Ctrl+R` for fzf history reverse search
- `up-arrow` for partial string matching in history
- `TAB` for auto-completion with floating window
- fish-like autosuggestions
- has the ability to build custom key binding and its callback function by modifying `geprc.py`

## How to install it?

Make sure you have GDB 8.0 or higher compiled with Python3.6+ bindings, then:

1. Install fzf: [Installation](https://github.com/junegunn/fzf#installation)

2. Download this plug-in and install it:

```shell
git clone https://github.com/lebr0nli/GEP.git && \
cd GEP && \
sh install.sh
```

> Note: This project is using prompt-toolkit 2.0.10 (because IDK why prompt-toolkit 3 is not working with GDB Python API), so the `install.sh` will download `prompt-toolkit==2.0.10` to `~/GEP/`.
> Maybe we can build our prompt toolkit just for this plug-in in the future.

3. Add the following text to the last line of your `~/.gdbinit`

```shell
source ~/GEP/.gdbinit-gep
```

4. Enjoy!

## For more configuration

You can modify configuration about history and auto-completion in `~/GEP/.gdbinit-gep`.

You can also add your custom key bindings by modifying `~/GEP/geprc.py`.

## A tiny side effect :(

The gdb event: `gdb.event.before_prompt` may be called only once, and this issue maybe will never, and can't be fixed.

So if you are using a GDB plug-in that is listening on this event, this plug-in will cause some bugs.

> As far as I know, pwndbg and gef won't be bothered by this side effect now.

To avoid this, you can change the callback function by adding them to `gdb.prompt_hook`, `gdb.prompt_hook` has almost the same effects with `event.before_prompt`, but `gdb.prompt_hook` can be directed invoke, so this plug-in still can emulate that callback for you!

## Bugs, suggestions, and ideas

If you found any bug or you have any suggestions/ideas about this plug-in, feel free to leave your feedback on the Github issue page or send me a pull request!

Thanks!
