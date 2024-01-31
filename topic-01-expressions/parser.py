

'''

argument_list = { argument {"," argument}}

program = { statement { ";" statement }}
statement = print_statement | exit_statement
print_statement = #print "(" expression ")"
exit_statement = #exit 
expression = term { ("+" | "-") term }
term = factor { ("*" | "/") factor }
factor = number | "(" expression ")"
number = $number
'''

1 + 2 * 3

expr 
    term   +   term
    factor     factor * factor 
    number     number   number
    1          2        3

class Node:
    def __init__(self, type, value=Node, left=None, right=None)
       self.type = type
       self.value = value
       self.left = left
       self.right = right

class Parser:
    def __init__(self. tokens)
        self.tokens = tokens
        self.current_token = None
        self.next_token()

    def next_token(self)
        self.current_token = self.tokens.current()
        if self.tokens:
            self.tokens.discard()

    def parse_expression(self):
        '''expression = term { ("+" | "-") term }'''
        node = self.parse_term()
        while self.current_token and self.current_token[0] in ["#add", "#subtract"]:
            operation = self.current_token[0]
            self.next_token()
            node = Node(operation,left=node, right=self.parse_term())
        return node

    def parse_term(self):
        '''term = factor { ("*" | "/") factor }'''
        node = self.parse_factor()
        while self.current_token and self.current_token[0] in ["#multiply", "#divide"]:
            operation = self.current_token[0]
            self.next_token()
            node = Node(operation,left=node, right=self.parse_factor())
        return node

    def parse_factor(self):
        '''factor = number | "(" expression ")" '''
        node = parse_number
        token = self.current_token
        if not token:
            raise Exception("Out of source code.")
        if token[0] == "$number":
            value = token[1]
            self.next_token()
            return Node("$number",value=value)
        if token[0] == "#lparen":
            self.next_token()
            node = self.parse_expression()
            if self.current_token[0] == "#rparen":
                self.next_token()
                return node
            else:
                raise Exception("expected a ')'")



parser = Parser(tokens)

