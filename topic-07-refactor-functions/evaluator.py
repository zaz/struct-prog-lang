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

    if ast["tag"] == "<function_call>":
        assert "identifier" in ast
        assert "arguments" in ast
        function, environment = evaluate_expression(ast["identifier"], environment)
        assert function["tag"] == "function"
        assert "parameters" in function
        assert "body" in function
        # match the parameters to arguments
        local_environment = {}
        parameters = function["parameters"]
        arguments = ast["arguments"]
        while parameters:
            assert arguments
            print(parameters, arguments)
            print(parameters["value"])
            arg, environment = evaluate(arguments, environment)
            local_environment[parameters["value"]] = arg
            parameters = parameters.get("next", None)
            arguments = arguments.get("next", None)
        assert parameters == None
        assert arguments == None
        local_environment["$parent"] = environment
        result, local_environment = evaluate(function["body"], local_environment)
        return result, environment

    if ast["tag"] == "return":
        print(ast)
        exit(0)

    # unary operations
    if ast["tag"] == "negate":
        value, environment = evaluate(ast["value"], environment)
        return -value, environment

    if ast["tag"] == "not":
        value, environment = evaluate(ast["value"], environment)
        if value:
            value = 0
        else:
            value = 1
        # left_value = 0 if left_value else 0
        return value, environment

    # binary operations
    if ast["tag"] == "+":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return left_value + right_value, environment
    if ast["tag"] == "-":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return left_value - right_value, environment
    if ast["tag"] == "*":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return left_value * right_value, environment
    if ast["tag"] == "/":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        # Add error handling for division by zero
        if right_value == 0:
            raise Exception("Division by zero")
        return left_value / right_value, environment
    if ast["tag"] == "*":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return left_value * right_value, environment
    if ast["tag"] == "<":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return int(left_value < right_value), environment
    if ast["tag"] == ">":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return int(left_value > right_value), environment
    if ast["tag"] == "<=":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return int(left_value <= right_value), environment
    if ast["tag"] == ">=":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return int(left_value >= right_value), environment
    if ast["tag"] == "==":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return int(left_value == right_value), environment
    if ast["tag"] == "!=":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return int(left_value != right_value), environment
    if ast["tag"] == "&&":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return int(left_value and right_value), environment
    if ast["tag"] == "||":
        left_value, environment = evaluate(ast["left"], environment)
        right_value, environment = evaluate(ast["right"], environment)
        return int(left_value or right_value), environment
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

    if ast["tag"] == "print":
        argument = ast.get("arguments", None)
        while argument:
            value, environment = evaluate_expression(argument, environment)
            print(value, end=" ")
            argument = argument.get("next", None)
        print()
        return None, environment

    return evaluate_expression(ast, environment)


def evaluate(ast, environment):
    return evaluate_statement(ast, environment)


from tokenizer import tokenize
from parser import parse


def equals(code, environment, expected_result, expected_environment=None):
    result, environment = evaluate(parse(tokenize(code)), environment)
    assert (
        result == expected_result
    ), f"""ERROR: When executing-- 
    {[code]},
    --expected--
    {[expected_result]},
    --got--
    {[result]}."""
    if expected_environment:
        assert (
            environment == expected_environment
        ), f"""
        ERROR: When executing 
        {[code]}, 
        expected
        {[expected_environment]},\n got \n{[environment]}.
        """


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
    equals("{x=4}", {}, None, {"x": 4})
    equals("{x=4; y=3}", {}, None, {"x": 4, "y": 3})
    equals("{x=4; y=3; y=1}", {}, None, {"x": 4, "y": 1})
    equals("{x=3; y=0; while (x>0) {x=x-1;y=y+1}}", {}, None, {"x": 0, "y": 3})


def test_evaluate_function_expression():
    print("test evaluate function_expression.")
    equals(
        "function(x) {return x}",
        None,
        {
            "tag": "function",
            "parameters": {"tag": "<identifier>", "value": "x"},
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
                "parameters": {"tag": "<identifier>", "value": "x"},
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
                "parameters": {"tag": "<identifier>", "value": "x"},
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

def test_evaluate_print_statement():
    print("test evaluate print_statement.")
    equals("print()", {}, None, None)
    equals("print(1)", {}, None, None)
    equals("print(1,2)", {}, None, None)
    equals("print(1,2,3+4)", {}, None, None)

def test_evaluate_function_call():
    print("test evaluate function call.")
    environment = {}
    code = "{f = function() {print(1)}; f()}"
    result, environment = evaluate(parse(tokenize(code)), environment)
    code = "{f = function() {print(1+2*4)}; f(); f();}"
    result, environment = evaluate(parse(tokenize(code)), environment)
    code = "{x=5; f = function() {print(x+x+x*2)}; f(); f();}"
    result, environment = evaluate(parse(tokenize(code)), environment)
    code = "{f = function(x) {print(x*x*x)}; f(2); f(3); f(4);}"
    result, environment = evaluate(parse(tokenize(code)), environment)
    code = "{z=100; f = function(x, y) {q=0.5; x=x*2;print(q*x*y*z)}; f(1,2); f(2,3); f(3,4);}"
    result, environment = evaluate(parse(tokenize(code)), environment)
    code = "{f = function(x, y) {return x+y;}; f(1,2); f(2,3); f(3,4);}"


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
    test_evaluate_unary_operators()
    test_evaluate_relational_operators()
    test_evaluate_logical_operators()
    test_evaluate_if_statement()
    test_evaluate_while_statement()
    test_evaluate_block_statement()
    test_evaluate_function_expression()
    test_evaluate_function_statement()
    test_evaluate_print_statement()
    test_evaluate_function_call()
    print("done.")
