

'''
expression = term { ("+" | "-") term }
term = factor { ("*" | "/") factor }
factor = number | "(" expression ")"
number = <number>
'''


def create_node(kind, left=None, right=None, value=None):
    return {
        "kind": kind,
        "value": value,
        "left": left,
        "right": right
    }

def parse_expression(tokens):
    node, tokens = parse_term(tokens)
    while tokens[0]["kind"] in ["+", "-"]:
        kind = tokens[0]["kind"]
        right_node, tokens = parse_term(tokens[1:])
        node = create_node(kind, left=node, right=right_node)
    return node, tokens

def parse_term(tokens):
    node, tokens = parse_factor(tokens)
    while tokens[0]["kind"] in ["*", "/"]:
        kind = tokens[0]["kind"]
        right_node, tokens = parse_factor(tokens[1:])
        node = create_node(kind, left=node, right=right_node)
    return node, tokens

def parse_factor(tokens):
    token = tokens[0]
    kind = token["kind"]
    if kind == "number":
        return create_node("number", value=token["value"]), tokens[1:] 
    if kind == "(":
        node, tokens = parse_expression(tokens[1:])
        if tokens and tokens[0]["kind"] != ")":
            raise Exception("Expected ')'")
        return node, tokens[1:]
    else:
        raise Exception(f"Unexpected token: {tokens[0]}")

def parse(tokens):
    tokens.append({"kind": None})  # Sentinel to mark the end of input
    ast, _ = parse_expression(tokens)
    return ast

from tokenizer import tokenize

def test_simple_addition_parsing():
    print("testing simple addition parsing...")
    tokens = tokenize("1+2")
    ast = parse(tokens)
    assert ast == {
        "kind": "+",
        "value": None,
        "left": {"kind": "number", "value": 1, "left": None, "right": None},
        "right": {"kind": "number", "value": 2, "left": None, "right": None},
    }


def test_nested_expressions_parsing():
    print("testing nested expressions parsing...")
    tokens = tokenize("(1+2)*3")
    ast = parse(tokens)
    assert ast == {
        "kind": "*",
        "value": None,
        "left": {
            "kind": "+",
            "value": None,
            "left": {"kind": "number", "value": 1, "left": None, "right": None},
            "right": {"kind": "number", "value": 2, "left": None, "right": None},
        },
        "right": {"kind": "number", "value": 3, "left": None, "right": None},
    }


def test_operation_precedence_parsing():
    print("testing operation precedence parsing...")
    tokens = tokenize("4-2/1")
    ast = parse(tokens)
    assert ast == {
        "kind": "-",
        "value": None,
        "left": {"kind": "number", "value": 4, "left": None, "right": None},
        "right": {
            "kind": "/",
            "value": None,
            "left": {"kind": "number", "value": 2, "left": None, "right": None},
            "right": {"kind": "number", "value": 1, "left": None, "right": None},
        },
    }


if __name__ == "__main__":
    test_simple_addition_parsing()
    test_nested_expressions_parsing()
    test_operation_precedence_parsing()
    print("done.")

