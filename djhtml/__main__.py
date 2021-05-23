import argparse
import sys

from . import modes


def verify_changed(source, result):
    """
    Verify that the source is either exactly equal to the result or
    that the result has only changed by added or removed whitespace.

    """
    output_lines = result.split("\n")
    for line_nr, line in enumerate(source.split("\n")):
        if line != output_lines[line_nr]:
            return True
        if line.strip() != output_lines[line_nr].strip():
            raise IndentationError("Non-whitespace changes detected. Core dumped.")


def main():
    """
    Entrypoint for all 4 command-line tools. Typical usage:

        $ djhtml -i file1.html file2.html

    """
    Mode = modes.DjHTML
    if sys.argv[0].endswith("djtxt"):
        Mode = modes.DjTXT
    if sys.argv[0].endswith("djcss"):
        Mode = modes.DjCSS
    if sys.argv[0].endswith("djjs"):
        Mode = modes.DjJS

    exit_status = 0

    parser = argparse.ArgumentParser(
        description=(
            "DjHTML is a Django template indenter that works with mixed"
            " HTML/CSS/Javascript templates. It works similar to other"
            " code-formatting tools such as Black. The goal is to correctly"
            " indent already well-structured templates but not to fix broken"
            " ones."
        ),
    )
    parser.add_argument(
        "-i", "--in-place", action="store_true", help="modify files in-place"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="be quiet")
    parser.add_argument(
        "-t", "--tabwidth", metavar="N", type=int, default=4, help="tab width"
    )
    parser.add_argument(
        "-o",
        "--output-file",
        metavar="filename",
        default="-",
        help="output filename",
    )
    parser.add_argument(
        "input_files",
        metavar="filenames",
        nargs="*",
        type=argparse.FileType("r"),
        default=[sys.stdin],
        help="input filenames",
    )
    parser.add_argument("-d", "--debug", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.in_place and args.input_files[0].name == "<stdin>":
        sys.exit("I’m sorry Dave, I’m afraid I can’t do that")

    if len(args.input_files) > 1 and not args.in_place:
        sys.exit("Will not modify files in-place without -i option")

    for input_file in args.input_files:
        try:
            source = input_file.read()
        except Exception:
            print(f"\nFatal error while processing {input_file.name}\n")
            raise

        try:
            if args.debug:
                print(Mode(source).debug())
                sys.exit()
            result = Mode(source).indent(args.tabwidth)
        except SyntaxError as e:
            if not args.quiet:
                print(
                    f"Syntax error in {input_file.name}:"
                    f" {str(e) or e.__class__.__name__}",
                    file=sys.stderr,
                )
            exit_status = 1
            continue
        except Exception:
            print(
                f"\nFatal error while processing {input_file.name}\n\n"
                "    If you have time and are using the latest version, we\n"
                "    would very much appreciate if you opened an issue on\n"
                "    https://github.com/rtts/djhtml/issues\n"
            )
            raise
        finally:
            input_file.close()

        if verify_changed(source, result):
            if args.in_place:
                output_file = open(input_file.name, "w")
            elif args.output_file != "-":
                output_file = open(args.output_file, "w")
            else:
                if not args.quiet:
                    print(result, end="")
                sys.exit(0)  # YOLO
            output_file.write(result)
            if not args.quiet:
                print(
                    f"Successfully wrote {output_file.name}",
                    file=sys.stderr,
                )
        elif not args.quiet:
            if not args.in_place and args.output_file == "-":
                print(result, end="")
            else:
                print(
                    f"{input_file.name} is perfectly indented!",
                    file=sys.stderr,
                )

    sys.exit(exit_status)


if __name__ == "__main__":
    main()
