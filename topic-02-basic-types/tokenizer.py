import re

# simple list class to hold token buffer
class List:
    def __init__(this, tokens):
        assert type(tokens) is list
        this.list = tokens

    def current(this):
        try:
            return this.list[0]
        except:
            return None

    def discard(this, token=None):
        if token:
            assert this.list[0] == token
        this.list = this.list[1:]

patterns = [
    [r"\s+", None],  # Whitespace
    [r"\d+(\.\d*)?", "$number"],
    [r"\+","#add"],
    [r"-","#subtract"],
    [r"\*","#multiply"],
    [r"/","#divide"],
    [r"\(","#lparen"],
    [r"\)","#rparen"],
    [r".", "$error"],  # unexpected content
]

def tokenize(characters):
    characters = characters + "\n"
    result = []
    pos = 0
    while pos < len(characters):
        for regex, token in patterns: 
            pattern = re.compile(regex)
            match = pattern.match(characters, pos)
            if match:
                break
        assert match
        pos = match.end()
        if token == None:
            continue
        result.append([token, match.group(0)])
    return List(result)

def test_simple_tokens():
    cases = [
        ["+",[['#add', '+']]],
        ["-",[['#subtract', '-']]],
        ["*",[['#multiply', '*']]],
        ["/",[['#divide', '/']]],
        ["(",[['#lparen', '(']]],
        [")",[['#rparen', ')']]]
    ]
    for text, tokens in cases:
        assert tokenize(text).list == tokens

def test_number_tokens():
    cases = [
        ["1",[['$number', '1']]],
        ["12",[['$number', '12']]],
        ["123",[['$number', '123']]],
        ["12.3",[['$number', '12.3']]],
        ["123.",[['$number', '123.']]],
    ]
    for text, tokens in cases:
        assert tokenize(text).list == tokens

def test_token_sequences():
    cases = [
        ["1+2",[['$number', '1'], ['#add', '+'], ['$number', '2']]],
        ["(1+2)",[['#lparen', '('], ['$number', '1'], ['#add', '+'], ['$number', '2'], ['#rparen', ')']]],
        ["-2",[['#subtract', '-'], ['$number', '2']]]
    ]
    for text, tokens in cases:
        assert tokenize(text).list == tokens

if __name__ == "__main__":
    test_simple_tokens()
    test_number_tokens()
    test_token_sequences()
    print("done.")

