import argparse
import sys

from . import modes


def verify_changed(source, result):
    """
    Verify that the source is either exactly equal to the result or
    that the result has only changed by added or removed whitespace.

    """
    output_lines = result.split("\n")
    changed = False
    for line_nr, line in enumerate(source.split("\n")):
        if line != output_lines[line_nr]:
            changed = True
        if line.strip() != output_lines[line_nr].strip():
            raise IndentationError("Non-whitespace changes detected. Core dumped.")

    return changed


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
    changed_files = 0
    unchanged_files = 0

    parser = argparse.ArgumentParser(
        description=(
            "DjHTML is a fully automatic template indenter that works with mixed"
            " HTML/CSS/Javascript templates that contain Django or Jinja2 template"
            " tags. It works similar to other code-formatting tools such as Black and"
            " interoperates nicely with pre-commit. More information at"
            " https://github.com/rtts/djhtml"
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
        "input_filenames",
        metavar="filenames",
        nargs="*",
        default=["-"],
        help="input filenames",
    )
    parser.add_argument("-d", "--debug", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.in_place and "-" in args.input_filenames:
        sys.exit("I’m sorry Dave, I’m afraid I can’t do that")

    if len(args.input_filenames) > 1 and not args.in_place:
        sys.exit("Will not modify files in-place without -i option")

    for input_filename in args.input_filenames:

        # Read input file
        try:
            input_file = (
                sys.stdin if input_filename == "-" else open(input_filename, "r")
            )
            source = input_file.read()
        except Exception as e:
            exit_status = 1
            print(f"Error opening {input_filename}: {e}", file=sys.stderr)
            continue

        # Indent input file
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
                "    https://github.com/rtts/djhtml/issues\n",
                file=sys.stderr,
            )
            raise
        finally:
            input_file.close()

        changed = verify_changed(source, result)

        # Print to stdout and exit
        if not args.in_place and args.output_file == "-":
            if not args.quiet:
                print(result, end="")
            sys.exit(0)  # YOLO

        # Write output file and increment counter
        if changed:
            changed_files += 1
            if args.in_place:
                output_file = open(input_file.name, "w")
            else:
                output_file = open(args.output_file, "w")
            output_file.write(result)
            if not args.quiet:
                print(
                    f"reindented {output_file.name}",
                    file=sys.stderr,
                )
        else:
            unchanged_files += 1

    # Print final summary
    if not args.quiet:
        print("All done! \\o/", file=sys.stderr)
        if changed_files:
            if unchanged_files:
                print(
                    f"{changed_files} template{'s' if changed_files > 1 else ''}"
                    f" reindented, {unchanged_files}"
                    f" template{'s' if unchanged_files > 1 else ''} left unchanged.",
                    file=sys.stderr,
                )
            else:
                print(
                    f"{changed_files} template{'s' if changed_files > 1 else ''}"
                    " reindented.",
                    file=sys.stderr,
                )
        else:
            if unchanged_files:
                print(
                    f"{unchanged_files} template{'s' if unchanged_files > 1 else ''}"
                    " left unchanged.",
                    file=sys.stderr,
                )

    sys.exit(exit_status)


if __name__ == "__main__":
    main()
