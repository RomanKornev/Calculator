import unittest
import math

from math_parser import Parser, Node  # Replace with the actual module name


class TestMathExpressionParser(unittest.TestCase):

    def test_basic_operations(self):
        self.assertEqual(str(Parser("2 + 3").parse()), "(2.0 + 3.0)")
        self.assertEqual(str(Parser("4 - 1").parse()), "(4.0 - 1.0)")
        self.assertEqual(str(Parser("-4 - 1").parse()), "(-4.0 - 1.0)")
        self.assertEqual(str(Parser("-4 + 1").parse()), "(-4.0 + 1.0)")
        self.assertEqual(str(Parser("5 * 6").parse()), "(5.0 * 6.0)")
        self.assertEqual(str(Parser("8 / 2").parse()), "(8.0 / 2.0)")

    def test_operator_precedence(self):
        self.assertEqual(str(Parser("2 + 3 * 4").parse()), "(2.0 + (3.0 * 4.0))")
        self.assertEqual(str(Parser("(2 + 3) * 4").parse()), "((2.0 + 3.0) * 4.0)")
        self.assertEqual(str(Parser("-(2 + 3) * 4").parse()), "(-(2.0 + 3.0) * 4.0)")
        self.assertEqual(str(Parser("-(2 + 3) + 4").parse()), "(-(2.0 + 3.0) + 4.0)")
        self.assertEqual(str(Parser("-(2 + 3) - (2 + 2)").parse()), "(-(2.0 + 3.0) - (2.0 + 2.0))")

    def test_exponentiation(self):
        self.assertEqual(str(Parser("2 ^ 3").parse()), "(2.0 ^ 3.0)")

    def test_factorial(self):
        self.assertEqual(str(Parser("5!").parse()), "factorial(5.0)")

    def test_custom_operator(self):
        self.assertEqual(str(Parser("3 || 4").parse()), "(3.0 || 4.0)")

    def test_constants(self):
        self.assertEqual(str(Parser("pi").parse()), str(float(math.pi)))
        self.assertEqual(str(Parser("e").parse()), str(float(math.e)))

    def test_functions(self):
        self.assertEqual(str(Parser("sin(30)").parse()), "sin(30.0)")
        self.assertEqual(str(Parser("log(10, 2)").parse()), "log(10.0, 2.0)")

    def test_engineering_notation(self):
        self.assertEqual(str(Parser("1k").parse()), "1000.0")
        self.assertEqual(str(Parser("2.5M").parse()), "2500000.0")
        self.assertAlmostEqual(float(Parser("3.4n").parse()), 3.4e-09, 9)

    def test_complex_expression(self):
        expr = "sin(2 * pi * 4k)! + 3M + 5 || 6"
        parsed = str(Parser(expr).parse())
        expected = "(factorial(sin(2.0 * 3.141592653589793 * 4000.0)) + 3000000.0 + (5.0 || 6.0))"
        self.assertEqual(parsed, expected)


if __name__ == "__main__":
    unittest.main()