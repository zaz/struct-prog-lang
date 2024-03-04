import re

patterns = [
    [r"//.*\n", "comment"],  # Comment
    [r"\s+", None],  # Whitespace
    [r"\d*\.\d+|\d+\.\d*|\d+", "number"],  # numeric literals
    [r'"([^"]|"")*"', "string"],  # string literals
    [r"true|false", "boolean"],  # boolean literals
    [r"null", "null"],  # the null literal
    [r"function", "function"],  # function keyword
    [r"return", "return"],  # return keyword
    [r"if", "if"],  # if keyword
    [r"else", "else"],  # else keyword
    [r"while", "while"],  # while keyword
    [r"for", "for"],  # for keyword
    [r"break", "break"],  # for keyword
    [r"continue", "continue"],  # for keyword
    [r"print", "print"],  # print keyword
    [r"import", "import"],  # function keyword
    [r"extern", "extern"],  # function keyword
    [r"input", "input"],  # function keyword
    [r"exit", "exit"],  # exit keyword
    [r"\+", "+"],
    [r"--","--"],
    [r"-", "-"],
    [r"\*", "*"],
    [r"/", "/"],
    [r"\(", "("],
    [r"\)", ")"],
    [r"\{", "{"],
    [r"\}", "}"],
    [r"\;", ";"],
    [r"==", "=="],
    [r"!=", "!="],
    [r"<=", "<="],
    [r">=", ">="],
    [r"<", "<"],
    [r">", ">"],
    [r"\&\&","&&"],
    [r"\|\|","||"],
    [r"\!","!"],
    [r"=", "="],
    [r"\.", "."],
    [r"\[", "["],
    [r"\]", "]"],
    [r",", ","],
    [r"\;", ";"],
    [r"[a-zA-Z_][a-zA-Z0-9_]*", "identifier"],  # identifiers
    [r".", "error"],  # unexpected content
]

for pattern in patterns:
    pattern[0] = re.compile(pattern[0])


# The lex/tokenize function
def tokenize(characters):
    tokens = []
    position = 0
    while position < len(characters):
        # find the first token pattern that matches
        for pattern, tag in patterns:
            match = pattern.match(characters, position)
            if match:
                break
        # this should never fail, since the last pattern matches everything.
        assert match
        # skip whitespace and comments
        if tag == None:
            position = match.end()
            continue
        # get the value of the token
        if tag == "error":
            # complain about errors and throw exception
            raise Exception(f"Syntax error: illegal character : {[value]}")
        else:
            # package the token
            tokens.append({"tag": tag, "value": match.group(0), "position": position})
        # update position for next match
        position = match.end()
    # do some post-processing on strings and numbers and booleans
    for token in tokens:
        if token["tag"] == "string":
            token["value"] = token["value"][1:-1].replace('""', '"')
            continue
        if token["tag"] == "number":
            if "." in token["value"]:
                token["value"] = float(token["value"])
            else:
                token["value"] = int(token["value"])
            continue
        if token["tag"] == "boolean":
            token["value"] = 1 if token["value"] == "true" else 0
            continue
        if token["tag"] == "null":
            token["value"] = None
            continue
    return tokens


def test_simple_tokens():
    print("testing simple tokens...")
    examples = ".,[,],+,-,*,/,(,),{,},;,!,&&,||,<,>,<=,>=,==,!=".split(",")
    for example in examples:
        t = tokenize(example)[0]
        assert t["tag"] == example
        assert t["value"] == example
        assert t["position"] == 0
    example = "(*/ +-[]{})  "
    t = tokenize(example)
    example = example.replace(" ", "")
    n = len(example)
    assert len(t) == n
    for i in range(0, n):
        assert t[i]["value"] == example[i]


def test_number_tokens():
    print("testing number tokens...")
    for s in ["1", "22", "12.1", "0", "12.", "123145", ".1234"]:
        t = tokenize(s)
        assert len(t) == 1, f"got tokens = {t}"
        assert t[0]["tag"] == "number"
        assert t[0]["value"] == float(s)


def test_string_tokens():
    print("testing string tokens...")
    for s in ['"example"', '"this is a longer example"', '"an embedded "" quote"']:
        t = tokenize(s)
        assert len(t) == 1
        assert t[0]["tag"] == "string"
        # adjust for the embedded quote behaviour
        assert t[0]["value"] == s[1:-1].replace('""', '"')


def test_boolean_tokens():
    print("testing boolean tokens...")
    for s in ["true", "false"]:
        t = tokenize(s)
        assert len(t) == 1
        assert t[0]["tag"] == "boolean"
        assert t[0]["value"] == (
            s == "true"
        ), f"got {[t[0]['value']]} expected {[(s == 'true')]}"
    t = tokenize("null")
    assert len(t) == 1
    assert t[0]["tag"] == "null"
    assert t[0]["value"] == None


def test_identifier_tokens():
    print("testing identifier tokens...")
    for s in ["x", "y", "z", "alpha", "beta", "gamma"]:
        t = tokenize(s)
        assert len(t) == 1
        assert t[0]["tag"] == "identifier"
        assert t[0]["value"] == s


def test_whitespace():
    print("testing whitespace...")
    for s in ["1", "1  ", "  1", "  1  "]:
        t = tokenize(s)
        assert len(t) == 1
        assert t[0]["tag"] == "number"
        assert t[0]["value"] == 1


def verify_same_tokens(a, b):
    def remove_position(tokens):
        for t in tokens:
            t["position"] == None

    return remove_position(tokenize(a)) == remove_position(tokenize(b))


def test_multiple_tokens():
    print("testing multiple tokens...")
    assert tokenize("1+2") == [
        {"tag": "number", "value": 1, "position": 0},
        {"tag": "+", "value": "+", "position": 1},
        {"tag": "number", "value": 2, "position": 2},
    ]
    assert tokenize("1+2-3") == [
        {"tag": "number", "value": 1, "position": 0},
        {"tag": "+", "value": "+", "position": 1},
        {"tag": "number", "value": 2, "position": 2},
        {"tag": "-", "value": "-", "position": 3},
        {"tag": "number", "value": 3, "position": 4},
    ]

    assert tokenize("3+4*(5-2)") == [
        {"tag": "number", "value": 3, "position": 0},
        {"tag": "+", "value": "+", "position": 1},
        {"tag": "number", "value": 4, "position": 2},
        {"tag": "*", "value": "*", "position": 3},
        {"tag": "(", "value": "(", "position": 4},
        {"tag": "number", "value": 5, "position": 5},
        {"tag": "-", "value": "-", "position": 6},
        {"tag": "number", "value": 2, "position": 7},
        {"tag": ")", "value": ")", "position": 8},
    ]

    assert verify_same_tokens("3+4*(5-2)", "3 + 4 * (5 - 2)")
    assert verify_same_tokens("3+4*(5-2)", " 3 + 4 * (5 - 2) ")
    assert verify_same_tokens("3+4*(5-2)", "  3  +  4 * (5 - 2)  ")


def test_keywords():
    print("testing keywords...")
    for keyword in [
        "function",
        "return",
        "if",
        "else",
        "while",
        "for",
        "break",
        "continue",
        "extern",
        "import",  # (reserved for future use)
        "input",
        "print",
        "exit",
    ]:
        t = tokenize(keyword)
        assert len(t) == 1
        assert t[0]["tag"] == keyword, f"expected {keyword}, got {t[0]}"
        assert t[0]["value"] == keyword


def test_comments():
    print("testing comments...")
    assert verify_same_tokens("//comment\n", "\n")
    assert verify_same_tokens("//alpha//comment\n", "alpha\n")
    assert verify_same_tokens("1+5  //comment\n", "1+5  \n")
    assert verify_same_tokens('"beta"//comment\n', '"beta"\n')


if __name__ == "__main__":
    print("testing tokenizer.")
    test_simple_tokens()
    test_number_tokens()
    test_boolean_tokens()
    test_string_tokens()
    test_identifier_tokens()
    test_whitespace()
    test_multiple_tokens()
    test_keywords()
    test_comments()
    print("done.")
