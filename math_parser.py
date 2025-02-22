import re
import math
from typing import Union, List


def pct(x):
    return x/100


def apply_pct(x, y):
    return x * (1 + y / 100)


class Node:
    def __init__(self, op: str, operands: List[Union['Node', float, str]]):
        self.op = op
        self.operands = operands

    def __repr__(self):
        if len(self.operands) == 1:
            arg_str = f"{self.operands[0]}"
            if self.op == '-':
                return self.op + arg_str
            elif self.op == 'pct':
                return f"({arg_str}/100)"
            if arg_str.startswith('(') and arg_str.endswith(')'):
                return self.op + arg_str.replace(' , ', ', ')  # These are functions
            else:
                return f"{self.op}({arg_str})"
        if self.op == "//":
            den = '*'.join(f"{p}" for p in self.operands)
            div = '+'.join('*'.join(f'{q}' for j, q in enumerate(self.operands) if j != i) for i, p in enumerate(self.operands))
            out = f"({den}/({div}))"
            return out
        if self.op == "**":
            # Power of power is always made on the first operand. X^Y^Z = (X^Y)^Z = X^(Y*Z)
            if len(self.operands) > 2:
                exponent = '*'.join(f'{x}' for x in self.operands[1:])
                return f"({self.operands[0]}**({exponent}))"
            else:
                return f"({self.operands[0]}**{self.operands[1]})"
        if self.op == "apply_pct" and len(self.operands) == 2:
            y = str(self.operands[1])
            if y.startswith('-'):
                return f"({self.operands[0]} * (1 - {y[1:]}))"
            else:
                return "({0} * (1 + {1}))".format(*self.operands)

        return f"({f' {self.op} '.join(map(str, self.operands))})"


class Parser:
    ENGINEERING_PREFIXES = {
        'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3,
        'k': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12
    }
    CONSTANTS = {'e': math.e, 'pi': math.pi}
    OPERATORS = {"+", "-", "*", "/", "^", "(", ")", ",", "!", "%", "&"}
    FUNCTIONS = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'cotg': lambda x: math.cos(x)/math.sin(x),
                 'asin': math.asin, 'acos': math.acos, 'atan': math.atan, 'atan2': math.atan2,
                 'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
                 'asinh': math.asinh, 'acosh': math.acosh, 'atanh': math.atanh,
                 'log': math.log, 'ln': math.log, 'log10': math.log10,
                 'sqr': math.sqrt, 'sqrt': math.sqrt, 'factorial': math.factorial,
                 'abs': abs, 'round': round, 'floor': math.floor, 'ceil': math.ceil,
                 'pct': pct, 'apply_pct': apply_pct,
                 }

    def __init__(self, expression: str):
        self.tokens = self.tokenize(expression)
        self.index = 0

    def tokenize(self, expr: str):
        tokens = re.findall(r'0x[0-9a-fA-F]+|0b[01]+|\d*\.?\d+(?:[eE][+-]?\d+)?[jfpnumkMGT]?|[a-zA-Z]\w*|[+\-*/^&(),!%]', expr)
        processed_tokens = []
        for i, t in enumerate(tokens):
            if t in self.OPERATORS:
                processed_tokens.append(t)
            elif t in self.CONSTANTS:
                if i > 0 and isinstance(processed_tokens[-1], (int, float)):  # numbers before constants taken as *
                    processed_tokens.append("*")
                processed_tokens.append(self.CONSTANTS[t])
            elif re.match(r'\d+$', t):
                processed_tokens.append(int(t))
            elif re.match(r'0x[0-9A-F]+$', t, re.IGNORECASE):
                processed_tokens.append((int(t, 16)))
            elif re.match(r'0b[01]+$', t, re.IGNORECASE):
                processed_tokens.append((int(t, 2)))
            elif re.match(r'\d*\.?\d+(?:[eE][+-]?\d+)?j$', t):
                processed_tokens.append(complex(t))
            elif re.match(r'\d*\.?\d+(?:[eE][+-]?\d+)?[fpnumkMGT]$', t):
                value, prefix = float(t[:-1]), t[-1]
                processed_tokens.append(value * self.ENGINEERING_PREFIXES[prefix])
            elif re.match(r'\d*\.?\d+(?:[eE][+-]?\d+)?$', t):
                processed_tokens.append(t)
            else:
                if i > 0 and isinstance(processed_tokens[-1], (int, float)):  # numbers before functions taken as *
                    processed_tokens.append("*")
                processed_tokens.append(t)
        return processed_tokens

    def parse(self):
        return self.parse_expression()

    def parse_expression(self, min_precedence=0):
        operands = [self.parse_primary()]
        current_op = None

        while self.index < len(self.tokens):
            longer_operator = 0
            op = self.tokens[self.index]
            if op == "!":  # Factorial operator (unary)
                self.index += 1
                operands[-1] = Node("factorial", [operands[-1]])
                continue

            # Test for double operators like ** ; // or
            elif (op == '*' or op == '/' or op == '^') and \
                    self.index + 1 < len(self.tokens) and self.tokens[self.index+1] == op:
                if op != '^':
                    op += self.tokens[self.index+1]
                longer_operator += 1

            # Test for the %
            elif op == "%":
                next_token = self.tokens[self.index + 1] if self.index + 1 < len(self.tokens) else None
                # if x% or x% <operator> or x%) then
                if next_token is None or next_token in self.OPERATORS or next_token == ')':
                    #  divide the x by 100
                    operands[-1] = Node('pct', [operands[-1]])
                    self.index += 1
                    continue
                else:
                    # if x % y then apply the python's remainder operator
                    pass  # don't need to do anything

            elif op == '^':
                op = '**'

            precedence = self.get_precedence(op)
            if precedence < min_precedence or op == ")":
                break

            if current_op is None:
                current_op = op
            elif op != current_op:
                if precedence <= self.get_precedence(current_op):
                    # close this node
                    operands = [Node(current_op, operands)]
                    current_op = op
                else:
                    raise NotImplemented  # This should not be possible. Just a safe guard.

            self.index += 1 + longer_operator
            if self.index < len(self.tokens):
                operands.append(self.parse_expression(precedence + 1))

        if len(operands) >= 2 and current_op == '+' or current_op == '-':
            # Check if any argument is a percentage. If so, then apply percentage to the argument on the left
            i = 1
            while i < len(operands):
                if isinstance(operands[i], Node) and operands[i].op == 'pct':
                    # replace the addition by an apply percentage
                    if current_op == '-':
                        # invert the sign of the percentage to apply
                        operands[i] = Node('-', [operands[i]])
                    operands[i-1] = Node('apply_pct', [operands[i-1], operands[i]])
                    del operands[i]
                else:
                    i += 1
        if len(operands) == 1:
            return operands[0]
        return Node(current_op, operands)

    def parse_primary(self):
        token = self.tokens[self.index]

        if isinstance(token, float):
            self.index += 1
            return token

        if token == '-':
            # Negate the next tokens
            self.index += 1
            return Node(token, [self.parse_primary()])

        if token == "(":
            self.index += 1
            node = self.parse_expression()
            if self.index < len(self.tokens) and self.tokens[self.index] == ")":
                self.index += 1  # Consume ')'
            return node

        if isinstance(token, str) and self.index + 1 < len(self.tokens) and self.tokens[self.index + 1] == "(":
            if token not in self.FUNCTIONS:
                raise NameError(f"Function {token} not recognized")
            function_name = token
            self.index += 2  # Consume function name and '('
            arguments = [self.parse_expression()]
            self.index += 1  # Consume ')'
            return Node(function_name, arguments)

        self.index += 1
        return token

    def get_precedence(self, op):
        precedences = {
            "+": 1, "-": 1,
            "*": 2, "/": 2, "//": 2, "^": 2, "&": 2,
            "**": 3,
            "!": 4, "%": 4    # Factorial and percentage has high precedence
        }  # Factorial has high precedence
        return precedences.get(op, 0)


def evaluate(equation: str, environment: dict = None):
    parser = Parser(equation)
    ast = parser.parse()
    env = {}
    env.update(Parser.FUNCTIONS)
    env.update(environment)
    return eval(str(ast), env), ast


if __name__ == "__main__":
    def test_equation(equation):
        print("Testing :", equation)
        parser = Parser(equation)
        ast = parser.parse()
        print(ast)

    # Example Usage
    test_equation("sin(2 * pi * 4k)! + 3M + 5 || 6")
    test_equation("sin(2 pi 4k)! + 3M + 5 || 6")
    test_equation("-2 pi")
