# -*- coding: utf-8 -*-

from math import *
import re

try:
    from scipy.special import *
    from builtins import *

    c = binom
except Exception as e:
    pass

sqr = lambda x: x ** 2


def json_wox(title, subtitle, icon, action=None, action_params=None, action_keep=None):
    json = {
        'Title': title,
        'SubTitle': subtitle,
        'IcoPath': icon
    }
    if action and action_params and action_keep:
        json.update({
            'JsonRPCAction': {
                'method': action,
                'parameters': action_params,
                'dontHideAfterAction': action_keep
            }
        })
    return json


def format_result(result):
    if hasattr(result, '__call__'):
        # show docstring for other similar methods
        raise NameError
    if isinstance(result, str):
        return result
    if isinstance(result, int) or isinstance(result, float):
        if int(result) == float(result):
            return '{:,}'.format(int(result)).replace(',', ' ')
        else:
            return '{:,}'.format(round(float(result), 5)).replace(',', ' ')
    elif hasattr(result, '__iter__'):
        return '[' + ', '.join(list(map(format_result, list(result)))) + ']'
    else:
        return str(result)


def calculate(query):
    results = []
    # filter any special characters at start or end
    query = re.sub(r'(^[+\-*/=])|([+\-*/=(]$)', '', query)
    try:
        result = eval(query)
        formatted = format_result(result)
        results.append(json_wox(formatted,
                                '{} = {}'.format(query, result),
                                'Images/app.ico',
                                'change_query',
                                [str(result)],
                                True))
    except SyntaxError:
        # try to close parentheses
        opening_par = query.count('(')
        closing_par = query.count(')')
        if opening_par > closing_par:
            return calculate(query + ')'*(opening_par-closing_par))
        else:
            # let Wox keep previous result
            raise SyntaxError
    except NameError:
        # try to find docstrings for methods similar to query
        glob = set(filter(lambda x: 'Error' not in x and 'Warning' not in x and '_' not in x, globals()))
        help = list(sorted(filter(lambda x: query in x, glob)))[:6]
        for method in help:
            method_eval = eval(method)
            method_help = method_eval.__doc__.split('\n')[0] if method_eval.__doc__ else ''
            results.append(json_wox(method,
                                    method_help,
                                    'Images/app.ico',
                                    'change_query_method',
                                    [str(method)],
                                    True))
        if not help:
            # let Wox keep previous result
            raise NameError
    return results

from wox import Wox, WoxAPI


class Calculator(Wox):
    def query(self, query):
        return calculate(query)

    def change_query(self, query):
        WoxAPI.change_query(query)

    def change_query_method(self, query):
        WoxAPI.change_query(query + '(')


if __name__ == '__main__':
    Calculator()
