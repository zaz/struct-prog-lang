def evaluate_expression(ast, environment):

    # simple values
    if ast["tag"] == "<number>":
        assert type(ast["value"]) in [
            float,
            int,
        ], f"unexpected ast numeric value {ast['value']} type is a {type(ast['value'])}."
        return ast["value"], environment

    if ast["tag"] == "<identifier>":
        assert type(ast["value"]) in [
            str
        ], f"unexpected ast identifer value {ast['value']} type is a {type(ast['value'])}."
        current_environment = environment
        while current_environment:
            if ast["value"] in current_environment:
                return current_environment[ast["value"]], environment
            current_environment = current_environment.get("$parent", None)
        assert current_environment, f"undefined identifier {ast['value']} in expression"

    if ast["tag"] == "function":
        return ast, environment

    # unary operations
    if ast["tag"] == "negate":
        value, environment = evaluate(ast["value"], environment)
        return -value, environment
    elif ast["tag"] == "not":
        value, environment = evaluate(ast["value"], environment)
        if value:
            value = 0
        else:
            value = 1
        # left_value = 0 if left_value else 0
        return value, environment

    # binary operations
    left_value, environment = evaluate(ast["left"], environment)
    right_value, environment = evaluate(ast["right"], environment)

    if ast["tag"] == "+":
        return left_value + right_value, environment
    elif ast["tag"] == "-":
        return left_value - right_value, environment
    elif ast["tag"] == "*":
        return left_value * right_value, environment
    elif ast["tag"] == "/":
        # Add error handling for division by zero
        if right_value == 0:
            raise Exception("Division by zero")
        return left_value / right_value, environment
    elif ast["tag"] == "*":
        return left_value * right_value, environment
    elif ast["tag"] == "<":
        return int(left_value < right_value), environment
    elif ast["tag"] == ">":
        return int(left_value > right_value), environment
    elif ast["tag"] == "<=":
        return int(left_value <= right_value), environment
    elif ast["tag"] == ">=":
        return int(left_value >= right_value), environment
    elif ast["tag"] == "==":
        return int(left_value == right_value), environment
    elif ast["tag"] == "!=":
        return int(left_value != right_value), environment
    elif ast["tag"] == "&&":
        return int(left_value and right_value), environment
    elif ast["tag"] == "||":
        return int(left_value or right_value), environment
    else:
        raise Exception(f"Unknown operation: {ast['tag']}")


def evaluate_statement(ast, environment):

    if ast["tag"] == "block":
        value, environment = evaluate_statement(ast["statement"], environment)
        if ast.get("next"):
            value, environment = evaluate_statement(ast["next"], environment)
        return None, environment

    if ast["tag"] == "=":
        assert (
            ast["target"]["tag"] == "<identifier>"
        ), f"ERROR: Expecting identifier in assignment statement."
        identifier = ast["target"]["value"]

        assert ast["value"], f"ERROR: Expecting expression in assignment statement."
        value, environment = evaluate_expression(ast["value"], environment)

        environment[identifier] = value
        return None, environment

    if ast["tag"] == "if":
        condition, environment = evaluate_expression(ast["condition"], environment)
        if condition:
            _, environment = evaluate_statement(ast["then"], environment)
            return None, environment
        else:
            if ast.get("else", None):
                _, environment = evaluate_statement(ast["else"], environment)
                return None, environment
        return None, environment

    if ast["tag"] == "while":
        condition, environment = evaluate_expression(ast["condition"], environment)
        while condition:
            _, environment = evaluate_statement(ast["do"], environment)
            condition, environment = evaluate_expression(ast["condition"], environment)
        return None, environment

    return evaluate_expression(ast, environment)


def evaluate(ast, environment):
    print(ast)
    return evaluate_statement(ast, environment)


from tokenizer import tokenize
from parser import parse


def equals(code, environment, expected_result, expected_environment=None):
    result, environment = evaluate(parse(tokenize(code)), environment)
    assert (
        result == expected_result
    ), f"ERROR: When executing {[code]}, expected\n {[expected_result]},\n got \numeric{[result]}."
    if expected_environment:
        assert (
            environment == expected_environment
        ), f"""
        ERROR: When executing 
        {[code]}, 
        expected
        {[expected_environment]},\n got \n{[environment]}."


def test_evaluate_single_value():
    print("test evaluate single value")
    equals("4", {}, 4, {})


def test_evaluate_single_identifier():
    print("test evaluate single identifier")
    equals("x", {"x": 3}, 3)
    equals("y", {"x": 3, "$parent": {"y": 4}}, 4)
    equals("z", {"x": 3, "$parent": {"y": 4, "$parent": {"z": 5}}}, 5)


def test_evaluate_simple_assignment():
    print("test evaluate simple assignment")
    equals("x=3", {}, None, {"x": 3})


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


def test_evaluate_unary_operators():
    print("test evaluate unary operators.")
    equals("-5", {}, -5)
    equals("!0", {}, 1)
    equals("!1", {}, 0)


def test_evaluate_relational_operators():
    print("test evaluate relational operators.")
    equals("2<3", {}, 1)
    equals("4==4", {}, 1)
    equals("4==1", {}, 0)


def test_evaluate_logical_operators():
    print("test evaluate logical operators.")
    equals("1==1", {}, 1)
    equals("1!=1", {}, 0)
    equals("1&&1", {}, 1)
    equals("1&&0", {}, 0)
    equals("0&&0", {}, 0)
    equals("1||1", {}, 1)
    equals("1||0", {}, 1)
    equals("0||0", {}, 0)
    equals("!1", {}, 0)
    equals("!0", {}, 1)


def test_evaluate_division_by_zero():
    print("test evaluate division by zero.")
    try:
        equals("1/0", {}, None)
        assert False, "Expected a division by zero error"
    except Exception as e:
        assert str(e) == "Division by zero"


def test_evaluate_if_statement():
    print("test evaluate if statement.")
    equals("if (1) x=4", {"x": 0}, None, {"x": 4})


def test_evaluate_while_statement():
    print("test evaluate while statement.")
    equals("while (0) x=4", {"x": 0}, None, {"x": 0})
    equals("while (x>0) {x=x-1;y=y+1}", {"x": 3, "y": 0}, None, {"x": 0, "y": 3})


def test_evaluate_block_statement():
    print("test evaluate block statement.")
    equals("{x=4}", {}, 4, {"x": 4})
    equals("{x=4; y=3}", {}, 3, {"x": 4, "y": 3})
    equals("{x=4; y=3; y=1}", {}, 1, {"x": 4, "y": 1})
    equals("{x=3; y=0; while (x>0) {x=x-1;y=y+1}}", {}, None, {"x": 0, "y": 3})


def debug_equals(code, environment, expected_result, expected_environment=None):
    tokens = tokenize(code)
    ast = parse(tokens)
    result, environment = evaluate(ast, environment)
    assert (
        result == expected_result
    ), f"ERROR: When executing {[code]}, expected {[expected_result]}, got {[result]}."
    if expected_environment:
        assert (
            environment == expected_environment
        ), f"ERROR: When executing {[code]}, expected {[expected_environment]}, got {[environment]}."


def test_evaluate_function_expression():
    print("test evaluate function_expression.")
    equals(
        "function(x) {return x}",
        None,
        {
            "tag": "function",
            "arguments": {"tag": "<identifier>", "value": "x"},
            "body": {
                "tag": "block",
                "statement": {
                    "tag": "return",
                    "value": {"tag": "<identifier>", "value": "x"},
                },
            },
        },
        None,
    )
    equals(
        "f = function(x) {return x}",
        {},
        None,
        {
            "f": {
                "tag": "function",
                "arguments": {"tag": "<identifier>", "value": "x"},
                "body": {
                    "tag": "block",
                    "statement": {
                        "tag": "return",
                        "value": {"tag": "<identifier>", "value": "x"},
                    },
                },
            },
        },
    )


def test_evaluate_function_statement():
    print("test evaluate function_statement.")
    equals(
        "function f(x) {return x}",
        {},
        None,
        {
            "f": {
                "tag": "function",
                "arguments": {"tag": "<identifier>", "value": "x"},
                "body": {
                    "tag": "block",
                    "statement": {
                        "tag": "return",
                        "value": {"tag": "<identifier>", "value": "x"},
                    },
                },
            },
        },
    )


def test_evaluate_function_call():
    print("test evaluate function call.")

    # equals(
    #     """
    #     {x=3; y=4}; function f(x) {return x+x};
    #     """,
    #     {},
    #     None,
    #     {"x": 3, "y": 4},
    # )

    equals(
        "{function f(x) {return x+x}; z=1}",
        {},
        None,
        {
            "f": {
                "tag": "function",
                "arguments": {"tag": "<identifier>", "value": "x"},
                "body": {
                    "tag": "block",
                    "statement": {
                        "tag": "return",
                        "value": {"tag": "<identifier>", "value": "x"},
                    },
                },
            },
            "z": 1,
        },
    )


if __name__ == "__main__":
    print("test evaluator...")
    # test_evaluate_single_value()
    # test_evaluate_single_identifier()
    # test_evaluate_simple_addition()
    # test_evaluate_simple_assignment()
    # test_evaluate_complex_expression()
    # test_evaluate_subtraction()
    # test_evaluate_division()
    # test_evaluate_division_by_zero()
    # test_evaluate_unary_operators()
    # test_evaluate_relational_operators()
    # test_evaluate_logical_operators()
    # test_evaluate_if_statement()
    # test_evaluate_while_statement()
    # test_evaluate_block_statement()
    # test_evaluate_function_expression()
    # test_evaluate_function_statement()
    test_evaluate_function_call()
    print("done.")
