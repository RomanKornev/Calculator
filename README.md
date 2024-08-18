# Calculator
Advanced calculator plugin for [Wox](http://www.getwox.com/).

Uses functions from ```math``` module and ```scipy.special``` (if installed).

![Calculator](http://i.imgur.com/nUztl4X.png)

Supported features:
- Function docstring and autocomplete
- Auto-closing parentheses
- Thousands separator
- List formatting
- Input filtering
- Copy to clipboard after pressing Enter (using `pyperclip` if available, thanks to @Jens-3302)
- Persistent storage of last result in variable `x`, (e.g., `1/x`) between sessions (thanks to @Jens-3302)
- Support for factorials with `5!` or `(3+2)!` (thanks to @Jens-3302)
- Support for `^` as power and `xor` as bitwise XOR (thanks to @Jens-3302)
- Implied multiplication handling (e.g., `2pi` becomes `2*pi`) (thanks to @Jens-3302)

***Protip***: use ```=``` sign to filter any unneccesary results:

```=2+2``` or ```2+2=```

## Installation
[Get Wox](http://www.getwox.com/)

To install the plugin, type in Wox:
```
wpm install Python Calculator
```

Install ```scipy``` to enable advanced calculations:
```
pip install scipy
```

## Security
Plugin uses ```eval``` function which opens up a potential vector for injection attacks.

Be careful when entering untrusted input.
