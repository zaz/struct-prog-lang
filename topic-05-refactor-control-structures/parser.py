"""
if_statement == "if" "(" logical_expression ")" statement (else statment)
while_statment == "while" "(" logical_expression ")" statement
block_statement = "{" {";"} [ statement { ";" {";"} statement } {";"} ] "}"
statement = ( if_statement | while_statement | block_statement | assignment | expression )
assignment = identifier "=" expression
arithmetic_expression = term { ("+" | "-") term }
relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression}
logical_expression = logical_term { "||" logical_term }
logical_term = logical_factor {"&&" logical_factor}
logical_factor = relational_expression | "!" logical_factor
expression = logical_expression
term = factor { ("*" | "/") factor }
factor = number | identifier | "(" expression ")" | "-" factor | "!" factor
number = <number>
"""

""" 
AST FORMAT

{ "tag":"<op>","left":<expression_node>, "right":<expression_node>}
{ "tag":"negate/not","value":<expression_node>}
{ "tag":"=", "target":<node>, "value":<expression_node>}
{ "tag":"if", "condition":<expression_node>, 
    "then":<statement_node>,
    "else":<statement_node>}
{ "tag":"while", "condition":<expression_node>, 
    "do":<statement_node>}

"""


# def create_node(tag, left=None, right=None, value=None):
#     return {"tag": tag, "value": value, "left": left, "right": right}


def parse_if_statement(tokens):
    # if_statement == "if" "(" logical_expression ")" statement
    assert tokens[0]["tag"] == "if"
    tokens = tokens[1:]
    if tokens[0]["tag"] != "(":
        raise Exception(f"Expected '(': {tokens[0]}")
    condition, tokens = parse_logical_expression(tokens[1:])
    if tokens[0]["tag"] != ")":
        raise Exception(f"Expected '(': {tokens[0]}")
    then_statement, tokens = parse_statement(tokens[1:])
    node = {
        "tag": "if",
        "condition": condition,
        "then": then_statement,
    }
    if tokens[0]["tag"] == "else":
        node["else"], tokens = parse_statement(tokens[1:])
    return node, tokens


def parse_while_statement(tokens):
    # while_statment == "while" "(" logical_expression ")" statement
    assert tokens[0]["tag"] == "while"
    tokens = tokens[1:]
    if tokens[0]["tag"] != "(":
        raise Exception(f"Expected '(': {tokens[0]}")
    condition, tokens = parse_logical_expression(tokens[1:])
    if tokens[0]["tag"] != ")":
        raise Exception(f"Expected '(': {tokens[0]}")
    statement, tokens = parse_statement(tokens[1:])
    return {"tag": "while", "condition": condition, "do": statement}, tokens


def parse_block_statement(tokens):
    # block_statement = "{" {";"} [ statement { ";" {";"} statement } {";"} ] "}"
    assert tokens[0]["tag"] == "{"
    tokens = tokens[1:]
    node = {"tag": "block"}
    first_node = node
    while tokens[0]["tag"] == ";":
        tokens = tokens[1:]
    if tokens[0]["tag"] != "}":
        statement, tokens = parse_statement(tokens)
        node["statement"] = statement
        while tokens[0]["tag"] == ";":
            while tokens[0]["tag"] == ";":
                tokens = tokens[1:]
            if tokens[0]["tag"] != "}":
                statement, tokens = parse_statement(tokens)
                node["next"] = {"tag": "block", "statement": statement}
                node = node["next"]
            assert tokens[0]["tag"] in [";","}"]
    assert tokens[0]["tag"] == "}"
    tokens = tokens[1:]
    return first_node, tokens


def parse_statement(tokens):
    # statement = if_statement | while_statement | block_statement | assignment | expression
    tag = tokens[0]["tag"]
    # note: none of these consumes a token
    if tag == "if":
        return parse_if_statement(tokens)
    if tag == "while":
        return parse_while_statement(tokens)
    if tag == "{":
        return parse_block_statement(tokens)
    if tag == "<identifier>":
        if tokens[1]["tag"] == "=":
            return parse_assignment(tokens)
    return parse_logical_expression(tokens)


def parse_assignment(tokens):
    if tokens[0]["tag"] != "<identifier>":
        raise Exception(f"Expected identifier: {tokens[0]}")
    identifier = {"tag": "<identifier>", "value": tokens[0]["value"]}
    tokens = tokens[1:]
    if tokens[0]["tag"] != "=":
        raise Exception(f"Expected '=': {tokens[0]}")
    expression, tokens = parse_logical_expression(tokens[1:])
    return {"tag": "=", "target": identifier, "value": expression}, tokens


def parse_relational_expression(tokens):
    node, tokens = parse_arithmetic_expression(tokens)
    while tokens[0]["tag"] in ["<", ">", "<=", ">=", "==", "!="]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_arithmetic_expression(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def parse_arithmetic_expression(tokens):
    node, tokens = parse_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def parse_term(tokens):
    node, tokens = parse_factor(tokens)
    while tokens[0]["tag"] in ["*", "/"]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def parse_factor(tokens):
    token = tokens[0]
    tag = token["tag"]
    if tag == "<number>":
        return {"tag": "<number>", "value": token["value"]}, tokens[1:]
    if tag == "<boolean>":
        return {"tag": "<boolean>", "value": token["value"]}, tokens[1:]
    if tag == "<identifier>":
        return {"tag": "<identifier>", "value": token["value"]}, tokens[1:]
    if tag == "(":
        node, tokens = parse_relational_expression(tokens[1:])
        if tokens and tokens[0]["tag"] != ")":
            raise Exception("Expected ')'")
        return node, tokens[1:]
    if tag == "-":
        node, tokens = parse_factor(tokens[1:])
        return {"tag": "negate", "value": node}, tokens
    raise Exception(f"Unexpected token: {tokens[0]}")


def parse_logical_expression(tokens):
    # logical_expression = logical_term { "||" logical_term }
    node, tokens = parse_logical_term(tokens)
    while tokens[0]["tag"] == "||":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def parse_logical_term(tokens):
    # logical_term = logical_factor {"&&" logical_factor}
    node, tokens = parse_logical_factor(tokens)
    while tokens[0]["tag"] == "&&":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def parse_logical_factor(tokens):
    # logical_factor = relational_expression | "!" logical_factor
    token = tokens[0]
    if token["tag"] == "!":
        node, tokens = parse_logical_factor(tokens[1:])
        return {"tag": "not", "value": node}, tokens
    return parse_relational_expression(tokens)


def parse(tokens):
    tokens.append({"tag": None})  # Sentinel to mark the end of input
    ast, _ = parse_statement(tokens)
    return ast


def format(ast, indent=0):
    indentation = " " * indent
    if ast["tag"] in ["<number>", "<boolean>", "<identifier>"]:
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
        "left": {"tag": "<number>", "value": 1},
        "right": {"tag": "<number>", "value": 2},
    }


def test_simple_identifier_parsing():
    print("test simple identifier parsing...")
    tokens = tokenize("x+y")
    ast = parse(tokens)
    assert ast == {
        "tag": "+",
        "left": {"tag": "<identifier>", "value": "x"},
        "right": {"tag": "<identifier>", "value": "y"},
    }


def test_boolean_parsing():
    print("test boolean parsing...")
    for token_identifer in ["true", "false"]:
        tokens = tokenize(token_identifer)
        value = tokens[0]["value"]
        ast = parse(tokens)
        assert ast == {"tag": "<boolean>", "value": value}


def test_logical_operators_parsing():
    print("test logical operators parsing")
    for op in ["==", "!=", "||", "&&"]:
        tokens = tokenize(f"1{op}0")
        ast = parse(tokens)
        assert ast == {
            "tag": op,
            "left": {"tag": "<number>", "value": 1},
            "right": {"tag": "<number>", "value": 0},
        }, f"AST for op {op} got ast = {ast}"
    tokens = tokenize(f"1 || 0 && 1")
    ast = parse(tokens)
    assert ast == {
        "tag": "||",
        "left": {"tag": "<number>", "value": 1},
        "right": {
            "tag": "&&",
            "left": {"tag": "<number>", "value": 0},
            "right": {"tag": "<number>", "value": 1},
        },
    }
    tokens = tokenize(f"1 && 0 || 1")
    ast = parse(tokens)
    assert ast == {
        "tag": "||",
        "left": {
            "tag": "&&",
            "left": {"tag": "<number>", "value": 1},
            "right": {"tag": "<number>", "value": 0},
        },
        "right": {"tag": "<number>", "value": 1},
    }

    tokens = tokenize(f"1 || 0 || 0")
    ast = parse(tokens)
    assert ast == {
        "tag": "||",
        "left": {
            "tag": "||",
            "left": {"tag": "<number>", "value": 1},
            "right": {"tag": "<number>", "value": 0},
        },
        "right": {"tag": "<number>", "value": 0},
    }

    tokens = tokenize(f"1 && 0 && 0")
    ast = parse(tokens)
    assert ast == {
        "tag": "&&",
        "left": {
            "tag": "&&",
            "left": {"tag": "<number>", "value": 1},
            "right": {"tag": "<number>", "value": 0},
        },
        "right": {"tag": "<number>", "value": 0},
    }


def test_relational_operators_parsing():
    print("test relational operators parsing")
    for op in ["<", ">", "<=", ">="]:
        tokens = tokenize(f"1+2{op}3*4")
        ast = parse(tokens)
        assert ast == {
            "tag": op,
            "left": {
                "tag": "+",
                "left": {"tag": "<number>", "value": 1},
                "right": {"tag": "<number>", "value": 2},
            },
            "right": {
                "tag": "*",
                "left": {"tag": "<number>", "value": 3},
                "right": {"tag": "<number>", "value": 4},
            },
        }


def test_unary_operators_parsing():
    print("test unary operators parsing")
    tokens = tokenize("-1")
    ast = parse(tokens)
    assert ast == {
        "tag": "negate",
        "value": {"tag": "<number>", "value": 1},
    }
    tokens = tokenize("!1")
    ast = parse(tokens)
    assert ast == {
        "tag": "not",
        "value": {"tag": "<number>", "value": 1},
    }
    tokens = tokenize("-(3+4+x)")
    ast = parse(tokens)
    assert ast == {
        "tag": "negate",
        "value": {
            "tag": "+",
            "left": {
                "tag": "+",
                "left": {"tag": "<number>", "value": 3},
                "right": {"tag": "<number>", "value": 4},
            },
            "right": {"tag": "<identifier>", "value": "x"},
        },
    }
    tokens = tokenize("!(3+4+x)")
    ast = parse(tokens)
    assert ast == {
        "tag": "not",
        "value": {
            "tag": "+",
            "left": {
                "tag": "+",
                "left": {"tag": "<number>", "value": 3},
                "right": {"tag": "<number>", "value": 4},
            },
            "right": {"tag": "<identifier>", "value": "x"},
        },
    }


def test_nested_expressions_parsing():
    print("test nested expressions parsing...")
    tokens = tokenize("(1+2)*3")
    ast = parse(tokens)
    assert ast == {
        "tag": "*",
        "left": {
            "tag": "+",
            "left": {"tag": "<number>", "value": 1},
            "right": {"tag": "<number>", "value": 2},
        },
        "right": {"tag": "<number>", "value": 3},
    }


def test_operator_precedence_parsing():
    print("test operator precedence parsing...")
    tokens = tokenize("4-2/1")
    ast = parse(tokens)
    assert ast == {
        "tag": "-",
        "left": {"tag": "<number>", "value": 4},
        "right": {
            "tag": "/",
            "left": {"tag": "<number>", "value": 2},
            "right": {"tag": "<number>", "value": 1},
        },
    }


def test_assignment_parsing():
    print("test assignment parsing...")
    tokens = tokenize("x=5+3")
    ast = parse(tokens)
    assert ast == {
        "tag": "=",
        "target": {"tag": "<identifier>", "value": "x"},
        "value": {
            "tag": "+",
            "left": {"tag": "<number>", "value": 5},
            "right": {"tag": "<number>", "value": 3},
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
    assert (
        result == "=\n    z\n    -\n        4\n        /\n            x\n            y"
    )


def test_if_statement():
    print("test if statement...")
    tokens = tokenize("if(1)x=1")
    ast = parse(tokens)
    assert ast == {
        "tag": "if",
        "condition": {"tag": "<number>", "value": 1},
        "then": {
            "tag": "=",
            "target": {"tag": "<identifier>", "value": "x"},
            "value": {"tag": "<number>", "value": 1},
        },
    }
    tokens = tokenize("if(1){x=1}")
    ast = parse(tokens)
    assert ast == {
        "tag": "if",
        "condition": {"tag": "<number>", "value": 1},
        "then": {
            "tag": "block",
            "statement": {
                "tag": "=",
                "target": {"tag": "<identifier>", "value": "x"},
                "value": {"tag": "<number>", "value": 1},
            },
        },
    }
    tokens = tokenize("if(1){x=1}else{x=3}")
    ast = parse(tokens)
    assert ast == {
        "tag": "if",
        "condition": {"tag": "<number>", "value": 1},
        "then": {
            "tag": "block",
            "statement": {
                "tag": "=",
                "target": {"tag": "<identifier>", "value": "x"},
                "value": {"tag": "<number>", "value": 1},
            },
        },
        "else": {
            "tag": "block",
            "statement": {
                "tag": "=",
                "target": {"tag": "<identifier>", "value": "x"},
                "value": {"tag": "<number>", "value": 3},
            },
        },
    }


def test_while_statement():
    print("test while statement...")
    tokens = tokenize("while(1)x=1")
    ast = parse(tokens)
    assert ast == {
        "tag": "while",
        "condition": {"tag": "<number>", "value": 1},
        "do": {
            "tag": "=",
            "target": {"tag": "<identifier>", "value": "x"},
            "value": {"tag": "<number>", "value": 1},
        },
    }


def test_block_statement():
    print("test block statement...")
    for code in ["{x=1}", "{x=1;}", "{x=1;;}", "{;;x=1;;}"]:
        tokens = tokenize(code)
        ast = parse(tokens)
        assert ast == {
            "tag": "block",
            "statement": {
                "tag": "=",
                "target": {"tag": "<identifier>", "value": "x"},
                "value": {"tag": "<number>", "value": 1},
            },
        }
    for code in ["{x=1;y=2}", "{x=1;y=2;}", "{x=1;;y=2;}", "{;x=1;;y=2;}"]:
        tokens = tokenize(code)
        ast = parse(tokens)
        assert ast == {
            "tag": "block",
            "statement": {
                "tag": "=",
                "target": {"tag": "<identifier>", "value": "x"},
                "value": {"tag": "<number>", "value": 1},
            },
            "next": {
                "tag": "block",
                "statement": {
                    "tag": "=",
                    "target": {"tag": "<identifier>", "value": "y"},
                    "value": {"tag": "<number>", "value": 2},
                },
            },
        }
    tokens = tokenize("{x=1;y=2;z=3}")
    ast = parse(tokens)
    assert ast == {
        "tag": "block",
        "statement": {
            "tag": "=",
            "target": {"tag": "<identifier>", "value": "x"},
            "value": {"tag": "<number>", "value": 1},
        },
        "next": {
            "tag": "block",
            "statement": {
                "tag": "=",
                "target": {"tag": "<identifier>", "value": "y"},
                "value": {"tag": "<number>", "value": 2},
            },
            "next": {
                "tag": "block",
                "statement": {
                    "tag": "=",
                    "target": {"tag": "<identifier>", "value": "z"},
                    "value": {"tag": "<number>", "value": 3},
                },
            },
        },
    }
    saved_ast = ast
    tokens = tokenize("{x=1;y=2;z=3;}")
    ast = parse(tokens)
    assert ast == saved_ast


if __name__ == "__main__":
    test_simple_addition_parsing()
    test_simple_identifier_parsing()
    test_unary_operators_parsing()
    test_logical_operators_parsing()
    test_relational_operators_parsing()
    test_nested_expressions_parsing()
    test_operator_precedence_parsing()
    test_assignment_parsing()
    test_boolean_parsing()
    test_if_statement()
    test_while_statement()
    test_block_statement()
    print("done.")
