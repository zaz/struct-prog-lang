def evaluate(ast):
    # Base cases:
    # if the node is nonexistent, return 0 (for unary negation)
    if ast is None:
        return 0
    # if the node is a number, return its value as a float
    if ast['kind'] == 'number':
        assert type(ast['value']) in [float, int], f"unexpected ast numeric value {ast['value']} type is a {type(ast['value'])}."
        return ast['value']
    
    # Recursive cases: evaluate the left and right sub-trees and apply the operation
    left_value = evaluate(ast['left'])
    right_value = evaluate(ast['right'])
    
    if ast['kind'] == '+':
        return left_value + right_value
    elif ast['kind'] == '-':
        return left_value - right_value
    elif ast['kind'] == '*':
        return left_value * right_value
    elif ast['kind'] == '/':
        # Add error handling for division by zero
        if right_value == 0:
            raise Exception("Division by zero")
        return left_value / right_value
    else:
        raise Exception(f"Unknown operation: {ast['kind']}")

from tokenizer import tokenize
from parser import parse

def equals(code,expected_result):
    result = evaluate(parse(tokenize(code)))
    assert result == expected_result, f"ERROR: When executing {[code]}, expected {[expected_result]}, got {[result]}."

def test_evaluate_simple_addition():
    print("testing simple addition.")
    ast = {'kind': '+', 'left': {'kind': 'number', 'value': 1}, 'right': {'kind': 'number', 'value': 2}}
    assert evaluate(ast) == 3
    t = tokenize("1 + 3")
    ast = parse(t)
    assert evaluate(ast) == 4
    assert evaluate(parse(tokenize("1 + 4"))) == 5
    equals("1 + 4", 5)

def test_evaluate_unary_negation():
    print("testing unary negation.")
    ast = {'kind': '-', 'left': None, 'right': {'kind': 'number', 'value': 2}}
    assert evaluate(ast) == -2
    assert evaluate(parse(tokenize("-(1 + 3)"))) == -4
    assert evaluate(parse(tokenize("1 + (-4)"))) == -3

def test_evaluate_complex_expression():
    print("testing complex expression.")
    ast = {
        'kind': '*', 
        'left': {
            'kind': '+', 
            'left': {'kind': 'number', 'value': 1}, 
            'right': {'kind': 'number', 'value': 2}
        }, 
        'right': {'kind': 'number', 'value': 3}
    }
    assert evaluate(ast) == 9
    assert evaluate(parse(tokenize("(1+2)*3"))) == 9
    assert evaluate(parse(tokenize("(1+2)*(3+4)"))) == 21
    equals("(1+2)*(3+4)", 21)

def test_evaluate_subtraction():
    print("testing subtraction.")
    equals("11-5", 6)

def test_evaluate_division():
    print("testing division.")
    equals("15/5", 3)

def test_evaluate_division_by_zero():
    print("testing division by zero.")
    try:
        equals("1/0", None)
        assert False, "Expected a division by zero error"
    except Exception as e:
        assert str(e) == "Division by zero"

if __name__ == "__main__":
    print("testing evaluator.")
    test_evaluate_simple_addition()
    test_evaluate_unary_negation()
    test_evaluate_complex_expression()
    test_evaluate_subtraction()
    test_evaluate_division()
    test_evaluate_division_by_zero()
    print("done.")

