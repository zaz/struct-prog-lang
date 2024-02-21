from tokenizer import tokenize
from parser import parse, format
from evaluator import evaluate
import sys
import readline


def main():
    environment = {}
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        tokens = tokenize(line)
        ast = parse(tokens)
        print("---")
        print(format(ast))
        print("---")
        result, environment = evaluate(ast, environment)
        print(result)


if __name__ == "__main__":
    main()
