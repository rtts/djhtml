import sys

from .modes import HTML


def main():
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Usage: djhtml <file-to-indent>")
        sys.exit(1)

    current_mode = HTML
    current_level = 0

    with open(filename, "r") as f:
        lines = f.readlines()

    with open(filename, "w") as f:
        for line in lines:
            mode = current_mode(line.rstrip())
            f.write(mode.get_line(current_level) + "\n")
            current_level += mode.nextlevel
            current_mode = mode.nextmode


if __name__ == "__main__":
    main()
