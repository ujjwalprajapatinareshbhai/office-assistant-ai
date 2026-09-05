from simpleeval import simple_eval

def calculate(expression: str):
    """Safely evaluate a mathematical expression."""
    try:
        result = simple_eval(expression)
        return result
    except Exception as e:
        return f"Error: {e}"