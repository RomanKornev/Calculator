# Calculator
Advanced calculator plugin for [Wox](http://www.getwox.com/).

Uses fuctions from ```math``` module and ```scipy.special``` (if installed).

![Calculator](http://i.imgur.com/nUztl4X.png)

Supported features:
- Function docstring and autocomplete
- Auto-closing parentheses
- Thousands separator
- List formatting
- Input filtering
- Copy to clipboard after pressing Enter

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
