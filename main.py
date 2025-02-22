# -*- coding: utf-8 -*-
import os
import traceback
from math import atan2, degrees

try:
    import pyperclip
except ImportError:
    pyperclip = None

import math_parser

x = None

if pyperclip is not None:
    try:
        x = float(pyperclip.paste())
    except ValueError:
        pass

xFilePath = os.environ['TMP'] + os.sep + "wox_pycalc_x.txt"

if x is None:
    if os.path.exists(xFilePath):
        try:
            with open(xFilePath, "r") as xFile:
                x = float(xFile.read())
        except FileNotFoundError:
            x = 0


# TODO: Implement storing of variables. Eliminates = operators

def write_to_x(result):
    global x
    x = result
    try:
        with open(xFilePath, "w") as xFile:
            xFile.write(result)
    except:
        pass


def to_eng(value):
    e = 0
    p = 1
    while p < value:
        e += 1
        p *= 1000
    while p > value:
        e -= 1
        p /= 1000
    if -5 <= e < 0:
        suffix = "fpnum"[e]
    elif e == 0:
        suffix = ''
    elif e == 1:
        suffix = "k"
    elif e == 2:
        suffix = 'Meg'
    elif e == 3:
        suffix = 'Giga'
    else:
        return f'{value:E}'
    return f'{value * 1000 ** -e:g}{suffix:}'


def divide_groups_4(s: str) -> str:
    """Divides the text in segments of 4 characters separated by spaces. Division is right aligned."""
    first_space = len(s) % 4
    return s[:first_space] + " " + " ".join(s[i:i+4] for i in range(first_space, len(s), 4))


def format_result(result):
    if hasattr(result, '__call__'):
        # show docstring for other similar methods
        raise NameError
    if isinstance(result, str):
        return result
    if isinstance(result, int) or isinstance(result, float):
        if int(result) == float(result):
            return f'{int(result):,}'.replace(',', ' ')
        else:
            return f'{round(float(result), 5):,}'.replace(',', ' ')
    elif hasattr(result, '__iter__'):
        try:
            return '[' + ', '.join(list(map(format_result, list(result)))) + ']'
        except TypeError:
            import numpy as np
            # check if ndarray
            result = result.flatten()
            if len(result) > 1:
                return '[' + ', '.join(list(map(format_result, result.flatten()))) + ']'
            else:
                return format_result(np.asscalar(result))
    elif isinstance(result, bool):
        return 'True' if result else 'False'
    else:
        return str(result)


def calculate(query):
    results = []
    try:
        result, expression = math_parser.evaluate(query, {'x': x})
    except NameError or SyntaxError:
        pass
    except Exception as err:
        err_text = traceback.format_exc()
        results.append({
            "Title": f"Error: {type(err)}",
            "SubTitle": err_text,
            "IcoPath": "icons/app.png",
        })
    else:
        if isinstance(result, float):
            fmt = f"{result:,}".replace(',', ' ')
            eng_repr = to_eng(result)
            results.append({
                "Title": fmt,
                "SubTitle": f'{expression} = {eng_repr}',
                "IcoPath": "icons/app.png",
                "ContextData": result,
                "JsonRPCAction": {
                    'method': 'change_query',
                    'parameters': [fmt],
                    'dontHideAfterAction': True
                }
            })
        elif isinstance(result, int):
            fmt = f"{result:,}".replace(',', ' ')
            results.append({
                "Title": fmt,
                "SubTitle": f'{expression} = {result}',
                "IcoPath": "icons/app.png",
                "ContextData": result,
                "JsonRPCAction": {
                    'method': 'change_query',
                    'parameters': [fmt],
                    'dontHideAfterAction': True
                }
            })
        elif isinstance(result, complex):
            complex_repr = f'{result}'
            results.append({
                "Title": complex_repr,
                "SubTitle": f'{expression} = {complex_repr}',
                "IcoPath": "icons/app.png",
                "ContextData": complex_repr,
                "JsonRPCAction": {
                    'method': 'change_query',
                    'parameters': [complex_repr],
                    'dontHideAfterAction': True
                }
            })
            # Format as magnitude and angle
            deg = degrees(atan2(result.imag, result.real))
            complex_repr1 = f'mag:{abs(result)} deg:{deg}'
            results.append({
                "Title": complex_repr1,
                "SubTitle": f'{complex_repr} = {complex_repr1}',
                "IcoPath": "icons/clip.png",
                "JsonRPCAction": {
                    'method': 'copy_to_clipboard',
                    'parameters': [complex_repr1],
                    'dontHideAfterAction': False
                }
            })
        else:
            results.append({
                "Title": f"Unknown Type {type(result)} : {result}",
                "SubTitle": f'{expression} = {result}',
                "IcoPath": "icons/app.png",
                "ContextData": result
            })

    return results


from wox import Wox, WoxAPI


class Calculator(Wox):
    def query(self, query):
        return calculate(query)

    def context_menu(self, result):
        results = []
        if isinstance(result, float):
            fmt = f"{result:,}"
            eng_repr = to_eng(result)
            results.append({
                "Title": fmt.replace(',', ' '),
                "SubTitle": 'Normal',
                "IcoPath": "Icons/copy.png",
                "JsonRPCAction": {
                    'method': 'copy_to_clipboard',
                    'parameters': [fmt],
                    'dontHideAfterAction': False,
                }
            })
            if fmt != eng_repr:
                results.append({
                    "Title": eng_repr,
                    "SubTitle": "Engineering",
                    "IcoPath": "Images/copy.png",
                    "JsonRPCAction": {
                        'method': 'copy_to_clipboard',
                        'parameters': [eng_repr],
                        'dontHideAfterAction': False,
                    }
                })
        elif isinstance(result, int):
            fmt = f"{result:,}".replace(',', ' ')
            results.append({
                "Title": fmt,
                "SubTitle": 'Normal Representation',
                "IcoPath": "Images/copy.png",
                "JsonRPCAction": {
                    'method': 'copy_to_clipboard',
                    'parameters': [fmt],
                    'dontHideAfterAction': False,
                }
            })
            # Format as hex
            hex_repr = f'0x{result:X}'
            results.append({
                "Title": divide_groups_4(hex_repr),
                "SubTitle": 'Hexadecimal',
                "IcoPath": "Images/copy.png",
                "JsonRPCAction": {
                    'method': 'copy_to_clipboard',
                    'parameters': [hex_repr],
                    'dontHideAfterAction': False,
                }
            })
            if abs(result) < 2**32:
                # Format as bin
                bin_repr = f'0b{result:b}'
                results.append({
                    "Title": divide_groups_4(bin_repr),
                    "SubTitle": 'Binary',
                    "IcoPath": "Images/copy.png",
                    "JsonRPCAction": {
                        'method': 'copy_to_clipboard',
                        'parameters': [bin_repr],
                        'dontHideAfterAction': False,
                    }
                })
        elif isinstance(result, str):
            try:
                result = complex(result)
            except ValueError:
                results.append({
                    "Title": result,
                    "SubTitle": f"String",
                    "IcoPath": "Images/copy.png",
                    "JsonRPCAction": {
                        'method': 'copy_to_clipboard',
                        'parameters': [result],
                        'dontHideAfterAction': False
                    }
                })
            else:
                complex_repr = f'{result}'
                results.append({
                    "Title": complex_repr,
                    "SubTitle": 'Complex Form',
                    "IcoPath": "icons/app.png",
                    "JsonRPCAction": {
                        'method': 'change_query',
                        'parameters': [complex_repr],
                        'dontHideAfterAction': False,
                    }
                })
                # Format as magnitude
                mag = f"{abs(result)}"
                results.append({
                    "Title": f"{mag}",
                    "SubTitle": f"|{result}| = {mag}",
                    "IcoPath": "Images/copy.png",
                    "JsonRPCAction": {
                        'method': 'copy_to_clipboard',
                        'parameters': [mag],
                        'dontHideAfterAction': False,
                    }
                })
                rad = atan2(result.imag, result.real)
                srad = f"{rad}"
                results.append({
                    "Title": f"{srad}",
                    "SubTitle": f"angle({result}) = {srad} radians",
                    "IcoPath": "Images/copy.png",
                    "JsonRPCAction": {
                        'method': 'copy_to_clipboard',
                        'parameters': [srad],
                        'dontHideAfterAction': False,
                    }
                })
                deg = degrees(rad)
                sdeg = f"{deg}"
                results.append({
                    "Title": sdeg,
                    "SubTitle": f"angle({result}) = {sdeg} degrees",
                    "IcoPath": "Images/copy.png",
                    "JsonRPCAction": {
                        'method': 'copy_to_clipboard',
                        'parameters': [sdeg],
                        'dontHideAfterAction': False,
                    }
                })
        return results

    def change_query(self, query):
        # change query and copy to clipboard after pressing enter
        WoxAPI.change_query(query)
        write_to_x(query)
        self.copy_to_clipboard(query)

    def change_query_method(self, query):
        WoxAPI.change_query(query + '(')

    def store_result(self, query, result):
        WoxAPI.change_query(query)
        write_to_x(result)
        self.copy_to_clipboard(result)

    def copy_to_clipboard(self, text):
        if pyperclip is not None:
            pyperclip.copy(text)
        else:
            # Workaround
            cmd = 'echo ' + text.strip() + '| clip'
            os.system(cmd)


if __name__ == '__main__':
    Calculator()
