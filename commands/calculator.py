import ast
import operator

class CalculatorTool:
    """
    A safe calculator tool that evaluates math expressions using an AST parser
    instead of the dangerous eval() function.
    """
    def __init__(self):
        # Map AST node types to Python operator functions
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.USub: operator.neg,
        }

    def evaluate(self, expression: str) -> str:
        try:
            # Parse the string into an Abstract Syntax Tree
            node = ast.parse(expression, mode='eval').body
            result = self._eval_node(node)
            return str(result)
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
                raise TypeError(f"Unsupported operator: {type(node.op)}")
            return self.operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if type(node.op) not in self.operators:
                raise TypeError(f"Unsupported operator: {type(node.op)}")
            return self.operators[type(node.op)](operand)
        else:
            raise TypeError(f"Unsupported syntax: {type(node)}")
