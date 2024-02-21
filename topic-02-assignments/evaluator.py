def evaluate_expression(ast, environment):

    # simple values
    if ast['tag'] == 'number':
        assert type(ast['value']) in [float, int], f"unexpected ast numeric value {ast['value']} type is a {type(ast['value'])}."
        return ast['value'], environment
    
    if ast['tag'] == 'identifier':
        assert type(ast['value']) in [str], f"unexpected ast identifer value {ast['value']} type is a {type(ast['value'])}."
        assert ast['value'] in environment, f"undefined identifier {ast['value']} in expression"
        return environment[ast['value']], environment
    
    # unary operations


    # binary operations
    left_value, environment = evaluate(ast['left'], environment)
    right_value, environment = evaluate(ast['right'], environment)

    if ast['tag'] == '+':
        return left_value + right_value, environment
    elif ast['tag'] == '-':
        return left_value - right_value, environment
    elif ast['tag'] == '*':
        return left_value * right_value, environment
    elif ast['tag'] == '/':
        # Add error handling for division by zero
        if right_value == 0:
            raise Exception("Division by zero")
        return left_value / right_value, environment
    else:
        raise Exception(f"Unknown operation: {ast['tag']}")

def evaluate(ast, environment):
    if ast['tag'] == '=':
        assert ast['left']['tag'] == 'identifier', f"ERROR: Expecting identifier in assignment statement."
        identifier = ast['left']['value']

        assert ast['right'], f"ERROR: Expecting expression in assignment statement."
        value, environment = evaluate_expression(ast['right'], environment)

        environment[identifier] = value
        return None, environment

    return evaluate_expression(ast, environment)


from tokenizer import tokenize
from parser import parse

def equals(code, environment, expected_result, expected_environment=None):
    result, environment = evaluate(parse(tokenize(code)), environment)
    assert result == expected_result, f"ERROR: When executing {[code]}, expected {[expected_result]}, got {[result]}."
    if expected_environment:
        assert environment == expected_environment, f"ERROR: When executing {[code]}, expected {[expected_environment]}, got {[environment]}."

def test_evaluate_single_value():
    print("test evaluate single value")
    equals("4", {}, 4, {})

def test_evaluate_single_identifier():
    print("test evaluate single identifier")
    equals("x", {"x":3}, 3, {"x":3})

def test_evaluate_simple_assignment():
    print("test evaluate simple assignment")
    equals("x=3", {}, None, {"x":3})

def test_evaluate_simple_addition():
    print("test evaluate simple addition")
    equals("1 + 3", {}, 4)
    equals("1 + 4", {}, 5)


def test_evaluate_complex_expression():
    print("test evaluate complex expression")
    equals("(1+2)*(3+4)", {}, 21)

def test_evaluate_subtraction():
    print("test evaluate subtraction.")
    equals("11-5", {}, 6)

def test_evaluate_division():
    print("test evaluate division.")
    equals("15/5", {}, 3)

def test_evaluate_division_by_zero():
    print("test evaluate division by zero.")
    try:
        equals("1/0", {}, None)
        assert False, "Expected a division by zero error"
    except Exception as e:
        assert str(e) == "Division by zero"

if __name__ == "__main__":
    print("test evaluator...")
    test_evaluate_single_value()
    test_evaluate_single_identifier()
    test_evaluate_simple_addition()
    test_evaluate_simple_assignment()
    test_evaluate_complex_expression()
    test_evaluate_subtraction()
    test_evaluate_division()
    test_evaluate_division_by_zero()
    print("done.")

