import ast
import operator
from .base import BaseTool

class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculate"

    @property
    def description(self) -> str:
        return "Evaluates a basic mathematical expression (e.g. 25 * 10)."

    @property
    def parameters_schema(self) -> dict:
        return {"expression": "string"}

    def __init__(self):
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.USub: operator.neg,
        }

    def execute(self, expression: str = "", **kwargs) -> str:
        if not expression:
            return "Please provide an expression."
        try:
            node = ast.parse(expression, mode='eval').body
            result = self._eval_node(node)
            return f"Result: {result}"
        except ZeroDivisionError:
            return "Error: Cannot divide by zero."
        except Exception:
            return "Invalid math expression."

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise TypeError("Only numbers are supported")
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if type(node.op) not in self.operators:
                raise TypeError("Unsupported operator")
            return self.operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if type(node.op) not in self.operators:
                raise TypeError("Unsupported operator")
            return self.operators[type(node.op)](operand)
        else:
            raise TypeError("Unsupported syntax")
