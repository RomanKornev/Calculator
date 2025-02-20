import re
import math
from typing import Union, List


class Node:
    def __init__(self, op: str, operands: List[Union['Node', float, str]]):
        self.op = op
        self.operands = operands

    def __repr__(self):
        if len(self.operands) == 1:
            arg_str = f"{self.operands[0]}"
            if self.op == '-':
                return self.op + arg_str
            if arg_str.startswith('(') and arg_str.endswith(')'):
                return self.op + arg_str.replace(' , ', ', ')  # These are functions
            else:
                return f"{self.op}({arg_str})"
        if self.op == "//":
            den = '*'.join(f"{p}" for p in self.operands)
            div = '+'.join('*'.join(f'{q}' for j, q in enumerate(self.operands) if j != i) for i, p in enumerate(self.operands))
            out = f"({den}/({div}))"
            return out
        if self.op == "^" and len(self.operands) == 2:
            return "({0}**{1})".format(*self.operands)
        return f"({f' {self.op} '.join(map(str, self.operands))})"


class Parser:
    ENGINEERING_PREFIXES = {
        'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3,
        'k': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12
    }
    CONSTANTS = {'e': math.e, 'pi': math.pi}
    OPERATORS = {"+", "-", "*", "/", "^", "(", ")", ",", "!", "//"}
    FUNCTIONS = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'cotg': lambda x: math.cos(x)/math.sin(x),
                 'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
                 'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
                 'asinh': math.asinh, 'acosh': math.acosh, 'atanh': math.atanh,
                 'log': math.log, 'ln': math.log, 'log10': math.log10,
                 'sqr': math.sqrt, 'sqrt': math.sqrt, 'factorial': math.factorial,
                 }

    def __init__(self, expression: str):
        self.tokens = self.tokenize(expression)
        self.index = 0

    def tokenize(self, expr: str):
        tokens = re.findall(r'\d*\.?\d+(?:[eE][+-]?\d+)?[fpnumkMGT]?|[a-zA-Z]+|//|[+\-*/^(),!]', expr)
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
            elif re.match(r'(0x[0-9A-F]+)|([0-9A-F]+H)$', t, re.IGNORECASE):
                processed_tokens.append((int(t, 16)))
            elif re.match(r'0b[01]+$', t, re.IGNORECASE):
                processed_tokens.append((int(t, 2)))
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
            op = self.tokens[self.index]
            if op == "!":  # Factorial operator (unary)
                self.index += 1
                operands[-1] = Node("factorial", [operands[-1]])
                continue

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

            self.index += 1
            if self.index < len(self.tokens):
                operands.append(self.parse_expression(precedence + 1))

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
        precedences = {"+": 1, "-": 1, "*": 2, "/": 2, "//": 2, "^": 3, "!": 4}  # Factorial has high precedence
        return precedences.get(op, 0)


def evaluate(equation: str, environment: dict = None) -> float:
    parser = Parser(equation)
    ast = parser.parse()
    env = {}
    env.update(Parser.FUNCTIONS)
    env.update(environment)
    return eval(str(ast), env)


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
