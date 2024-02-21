"""
statement = assignment | expression
assignment = identifier "=" expression
expression = term { ("+" | "-") term }
term = factor { ("*" | "/") factor }
factor = number | identifier | "(" expression ")"
number = <number>
"""


def create_node(tag, left=None, right=None, value=None):
    return {"tag": tag, "value": value, "left": left, "right": right}


def parse_statement(tokens):
    # note: none of these consumes a token
    if tokens[0]["tag"] == "identifier":
        if tokens[1]["tag"] == "=":
            return parse_assignment(tokens)
    return parse_expression(tokens)


def parse_assignment(tokens):
    if tokens[0]["tag"] != "identifier":
        raise Exception(f"Expected identifier: {tokens[0]}")
    identifier = create_node("identifier", value=tokens[0]["value"])
    tokens = tokens[1:]
    if tokens[0]["tag"] != "=":
        raise Exception(f"Expected '=': {tokens[0]}")
    expression, tokens = parse_expression(tokens[1:])
    return create_node("=", left=identifier, right=expression), tokens


def parse_expression(tokens):
    node, tokens = parse_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_term(tokens[1:])
        node = create_node(tag, left=node, right=right_node)
    return node, tokens


def parse_term(tokens):
    node, tokens = parse_factor(tokens)
    while tokens[0]["tag"] in ["*", "/"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_factor(tokens[1:])
        node = create_node(tag, left=node, right=right_node)
    return node, tokens


def parse_factor(tokens):
    token = tokens[0]
    tag = token["tag"]
    if tag == "number":
        return create_node("number", value=token["value"]), tokens[1:]
    if tag == "identifier":
        return create_node("identifier", value=token["value"]), tokens[1:]
    if tag == "(":
        node, tokens = parse_expression(tokens[1:])
        if tokens and tokens[0]["tag"] != ")":
            raise Exception("Expected ')'")
        return node, tokens[1:]
    else:
        raise Exception(f"Unexpected token: {tokens[0]}")


def parse(tokens):
    tokens.append({"tag": None})  # Sentinel to mark the end of input
    ast, _ = parse_statement(tokens)
    return ast


def format(ast, indent=0):
    indentation = " " * indent
    if ast["tag"] in ["number", "identifier"]:
        return indentation + str(ast["value"])
    result = indentation + ast["tag"]
    if ast["left"]:
        result = result + "\n" + format(ast["left"], indent=indent + 4)
    if ast["right"]:
        result = result + "\n" + format(ast["right"], indent=indent + 4)
    return result


from tokenizer import tokenize


def test_simple_addition_parsing():
    print("test simple addition parsing...")
    tokens = tokenize("1+2")
    ast = parse(tokens)
    assert ast == {
        "tag": "+",
        "value": None,
        "left": {"tag": "number", "value": 1, "left": None, "right": None},
        "right": {"tag": "number", "value": 2, "left": None, "right": None},
    }


def test_simple_identifier_parsing():
    print("test simple identifier parsing...")
    tokens = tokenize("x+y")
    ast = parse(tokens)
    assert ast == {
        "tag": "+",
        "value": None,
        "left": {"tag": "identifier", "value": "x", "left": None, "right": None},
        "right": {"tag": "identifier", "value": "y", "left": None, "right": None},
    }


def test_nested_expressions_parsing():
    print("test nested expressions parsing...")
    tokens = tokenize("(1+2)*3")
    ast = parse(tokens)
    assert ast == {
        "tag": "*",
        "value": None,
        "left": {
            "tag": "+",
            "value": None,
            "left": {"tag": "number", "value": 1, "left": None, "right": None},
            "right": {"tag": "number", "value": 2, "left": None, "right": None},
        },
        "right": {"tag": "number", "value": 3, "left": None, "right": None},
    }


def test_operator_precedence_parsing():
    print("test operator precedence parsing...")
    tokens = tokenize("4-2/1")
    ast = parse(tokens)
    assert ast == {
        "tag": "-",
        "value": None,
        "left": {"tag": "number", "value": 4, "left": None, "right": None},
        "right": {
            "tag": "/",
            "value": None,
            "left": {"tag": "number", "value": 2, "left": None, "right": None},
            "right": {"tag": "number", "value": 1, "left": None, "right": None},
        },
    }


def test_assignment_parsing():
    print("test assignment parsing...")
    tokens = tokenize("x=5+3")
    ast = parse(tokens)
    assert ast == {
        "tag": "=",
        "value": None,
        "left": {"tag": "identifier", "value": "x", "left": None, "right": None},
        "right": {
            "tag": "+",
            "value": None,
            "left": {"tag": "number", "value": 5, "left": None, "right": None},
            "right": {"tag": "number", "value": 3, "left": None, "right": None},
        },
    }


def test_format_ast():
    print("test format AST...")
    tokens = tokenize("4-(2/1)")
    ast = parse(tokens)
    result = format(ast)
    assert result == "-\n    4\n    /\n        2\n        1"
    tokens = tokenize("4-(x/y)")
    ast = parse(tokens)
    result = format(ast)
    assert result == "-\n    4\n    /\n        x\n        y"
    tokens = tokenize("z=4-(x/y)")
    ast = parse(tokens)
    result = format(ast)
    print([result])
    assert result == "=\n    z\n    -\n        4\n        /\n            x\n            y"


if __name__ == "__main__":
    test_simple_addition_parsing()
    test_simple_identifier_parsing()
    test_nested_expressions_parsing()
    test_operator_precedence_parsing()
    test_assignment_parsing()
    print("done.")
