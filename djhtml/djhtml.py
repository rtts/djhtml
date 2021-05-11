from .modes import HTML


def djhtml_indent(lines):
    current_mode = HTML
    current_level = 0

    for line in lines:
        mode = current_mode(line.rstrip())
        yield mode.get_line(current_level) + "\n"
        current_level += mode.nextlevel
        current_mode = mode.nextmode
