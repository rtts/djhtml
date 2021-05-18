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
            " ones. A non-zero exit status indicates that a template could not"
            " be indented."
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
    args = parser.parse_args()

    if args.in_place and args.input_files[0].name == "<stdin>":
        sys.exit("I’m sorry Dave, I’m afraid I can’t do that")

    if len(args.input_files) > 1 and not args.in_place:
        sys.exit("Will not modify files in-place without -i option")

    for input_file in args.input_files:
        source = input_file.read()
        try:
            result = Mode(source).indent(args.tabwidth)
        except SyntaxError as e:
            if not args.quiet:
                print(
                    f"Error in {input_file.name}: {str(e) or e.__class__.__name__}",
                    file=sys.stderr,
                )
            exit_status = 1
            continue
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
            print(
                f"{input_file.name} is perfectly indented!",
                file=sys.stderr,
            )

    sys.exit(exit_status)


if __name__ == "__main__":
    main()
