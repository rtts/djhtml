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

    changed_files = 0
    unchanged_files = 0
    problematic_files = 0

    parser = argparse.ArgumentParser(
        description=(
            "DjHTML is a fully automatic template indenter that works with mixed"
            " HTML/CSS/Javascript templates that contain Django or Jinja template"
            " tags. It works similar to other code-formatting tools such as Black and"
            " interoperates nicely with pre-commit. Full documentation can be found at"
            " https://github.com/rtts/djhtml"
        ),
    )
    parser.add_argument(
        "-i", "--in-place", action="store_true", help="modify files in-place"
    )
    parser.add_argument("-c", "--check", action="store_true", help="don't modify files")
    parser.add_argument("-q", "--quiet", action="store_true", help="be quiet")
    parser.add_argument(
        "-t",
        "--tabwidth",
        metavar="N",
        type=int,
        default=4,
        help="tabwidth (default is 4)",
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

    if len(args.input_filenames) > 1 and not args.in_place and not args.check:
        sys.exit("Will not modify files in-place without -i option")

    for input_filename in args.input_filenames:

        # Read input file
        try:
            input_file = (
                sys.stdin if input_filename == "-" else open(input_filename, "r")
            )
            source = input_file.read()
        except Exception as e:
            problematic_files += 1
            if not args.quiet:
                print(f"Error opening {input_filename}: {e}", file=sys.stderr)
            continue

        # Indent input file
        try:
            if args.debug:
                print(Mode(source).debug())
                sys.exit()
            result = Mode(source).indent(args.tabwidth)
        except SyntaxError as e:
            problematic_files += 1
            if not args.quiet:
                print(
                    f"Syntax error in {input_file.name}:"
                    f" {str(e) or e.__class__.__name__}",
                    file=sys.stderr,
                )
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
        if not args.in_place and not args.check and args.output_file == "-":
            if not args.quiet:
                print(result, end="")
            sys.exit(1 if args.check and changed else 0)

        # Write output file
        if changed and args.check:
            changed_files += 1
        elif changed:
            output_filename = input_file.name if args.in_place else args.output_file
            try:
                output_file = open(output_filename, "w")
                output_file.write(result)
                output_file.close()
                changed_files += 1
            except Exception as e:
                problematic_files += 1
                if not args.quiet:
                    print(f"Error writing {output_filename}: {e}", file=sys.stderr)
                continue
            if not args.quiet:
                print(
                    f"reindented {output_file.name}",
                    file=sys.stderr,
                )
        else:
            unchanged_files += 1

    # Print final summary
    if not args.quiet:
        s = "s" if changed_files != 1 else ""
        have = "would have" if args.check else "have" if s else "has"
        print(
            f"{changed_files} template{s} {have} been reindented.",
            file=sys.stderr,
        )
        if unchanged_files:
            s = "s" if unchanged_files != 1 else ""
            were = "were" if s else "was"
            print(
                f"{unchanged_files} template{s} {were} already perfect!",
                file=sys.stderr,
            )
        if problematic_files:
            s = "s" if problematic_files != 1 else ""
            print(
                f"{problematic_files} template{s} could not be processed due to an"
                " error.",
                file=sys.stderr,
            )

    sys.exit(changed_files if args.check else problematic_files)


if __name__ == "__main__":
    main()
