from tokenizer import tokenize
from parser import parse
from evaluator import evaluate
import sys


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        tokens = tokenize(line)
        ast = parse(tokens)
        result = evaluate(ast)
        print(result)


if __name__ == "__main__":
    main()
