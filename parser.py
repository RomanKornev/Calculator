import re
import math
from typing import Union


class Node:
    def __init__(self, op: str, left: Union['Node', float, str], right: Union['Node', float, None] = None):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        if self.right is None:
            return f"{self.op}({self.left})"
        return f"({self.left} {self.op} {self.right})"


class Parser:
    ENGINEERING_PREFIXES = {
        'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3,
        'k': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12
    }
    CONSTANTS = {'e': math.e, 'pi': math.pi}

    def __init__(self, expression: str):
        self.tokens = self.tokenize(expression)
        self.index = 0

    def tokenize(self, expr: str):
        tokens = re.findall(r'\d+\.\d+|\d+|[a-zA-Z]+|\|?[+\-*/^()|,!]?', expr)
        processed_tokens = []
        for t in tokens:
            if t in {"+", "-", "*", "/", "^", "(", ")", "||", ",", "!"}:
                processed_tokens.append(t)
            elif t in self.CONSTANTS:
                processed_tokens.append(self.CONSTANTS[t])
            elif re.match(r'\d+[fpnumkMGT]$', t):
                value, prefix = float(t[:-1]), t[-1]
                processed_tokens.append(value * self.ENGINEERING_PREFIXES[prefix])
            elif re.match(r'\d+', t):
                processed_tokens.append(float(t))
            else:
                processed_tokens.append(t)
        return processed_tokens

    def parse(self):
        return self.parse_expression()

    def parse_expression(self, min_precedence=0):
        left = self.parse_primary()

        while self.index < len(self.tokens):
            op = self.tokens[self.index]
            precedence = self.get_precedence(op)

            if precedence < min_precedence:
                break

            if op == "!":  # Factorial operator (unary)
                self.index += 1
                left = Node("!", left)
                continue

            self.index += 1
            right = self.parse_expression(precedence + 1)
            left = Node(op, left, right)

        return left

    def parse_primary(self):
        token = self.tokens[self.index]

        if isinstance(token, float):
            self.index += 1
            return token

        if token == "(":
            self.index += 1
            node = self.parse_expression()
            self.index += 1  # Consume ')'
            return node

        if isinstance(token, str) and self.index + 1 < len(self.tokens) and self.tokens[self.index + 1] == "(":
            function_name = token
            self.index += 2  # Consume function name and '('
            argument = self.parse_expression()
            self.index += 1  # Consume ')'
            return Node(function_name, argument)

        self.index += 1
        return token

    def get_precedence(self, op):
        precedences = {"+": 1, "-": 1, "*": 2, "/": 2, "||": 2, "^": 3, "!": 4}  # Factorial has high precedence
        return precedences.get(op, 0)


if __name__ == "__main__":

    # Example Usage
    expr = "sin(2 * pi * 4k)! + 3M || 6"
    parser = Parser(expr)
    ast = parser.parse()
    print(ast)
