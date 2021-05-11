import sys

from .djhtml import djhtml_indent


def main():
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Usage: djhtml <file-to-indent>")
        sys.exit(1)

    with open(filename, "r") as f:
        lines = f.readlines()

    with open(filename, "w") as f:
        for line in djhtml_indent(lines):
            f.write(line)


if __name__ == "__main__":
    main()
