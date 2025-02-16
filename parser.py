import re
import math
from typing import Union, List


class Node:
    def __init__(self, op: str, operands: List[Union['Node', float, str]]):
        self.op = op
        self.operands = operands

    def __repr__(self):
        if len(self.operands) == 1:
            return f"{self.op}({self.operands[0]})"
        return f"({f' {self.op} '.join(map(str, self.operands))})"


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
        tokens = re.findall(r'\d*\.?\d+(?:[eE][+-]?\d+)?[fpnumkMGT]?|[a-zA-Z]+|\|\||//|[+\-*/^()|,!]', expr)
        processed_tokens = []
        for i, t in enumerate(tokens):
            if t in {"+", "-", "*", "/", "^", "(", ")", "||", ",", "!"}:
                processed_tokens.append(t)
            elif t in self.CONSTANTS:
                processed_tokens.append(self.CONSTANTS[t])
                if i > 0 and isinstance(processed_tokens[-2], float):
                    processed_tokens.insert(-1, "*")
            elif re.match(r'\d*\.?\d+(?:[eE][+-]?\d+)?[fpnumkMGT]$', t):
                value, prefix = float(t[:-1]), t[-1]
                processed_tokens.append(value * self.ENGINEERING_PREFIXES[prefix])
            elif re.match(r'\d*\.?\d+(?:[eE][+-]?\d+)?$', t):
                processed_tokens.append(float(t))
            else:
                processed_tokens.append(t)
                if i > 0 and isinstance(processed_tokens[-2], float):
                    processed_tokens.insert(-1, "*")
        return processed_tokens

    def parse(self):
        return self.parse_expression()

    def parse_expression(self, min_precedence=0):
        operands = [self.parse_primary()]

        while self.index < len(self.tokens):
            op = self.tokens[self.index]
            precedence = self.get_precedence(op)

            if precedence < min_precedence or op == ')':
                break

            if op == "!":  # Factorial operator (unary)
                self.index += 1
                operands = [Node("!", operands)]
                continue

            self.index += 1
            operands.append(self.parse_expression(precedence + 1))

            # Group same-precedence operators together
            if len(operands) > 1 and all(isinstance(o, Node) and o.op == op for o in operands[:-1]):
                operands = operands[:-1] + operands[-1].operands

        return Node(op, operands) if len(operands) > 1 else operands[0]

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
            arguments = [self.parse_expression(0)]
            while self.index < len(self.tokens) and self.tokens[self.index] == ",":
                self.index += 1
                arguments.append(self.parse_expression())
            self.index += 1  # Consume ')'
            return Node(function_name, arguments)

        self.index += 1
        return token

    def get_precedence(self, op):
        precedences = {"+": 1, "-": 1, "*": 2, "/": 2, "||": 2, "^": 3, "!": 4}  # Factorial has high precedence
        return precedences.get(op, 0)


# Example Usage
expr = "sin(2 * pi * 4k)! + 3M + 5 || 6"
parser = Parser(expr)
ast = parser.parse()
print(ast)
