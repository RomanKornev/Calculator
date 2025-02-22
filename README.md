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
- Support for `^` as power. xor is supported as ^^ operator
- Implied multiplication handling (e.g., `2pi` becomes `2*pi`) (thanks to @Jens-3302)
- Use // for making parallel between resistors
- The % operator can be use to add or subtract a percentage from a value. Example: X+Y% will make X*(1+Y/100)
- Supports engineering notation for values. Example: 10p means 10E-12.
- Supports operations with complex numbers
- support of the context menu in WOX, allowing it to show integer values in HEX, BINARY, floating points with 
  engineering notation and complex numbers with magnitude and angle of the corresponding vector.


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

## Notes
The | operator is used by wox on the searches. So it can be used for calculations.