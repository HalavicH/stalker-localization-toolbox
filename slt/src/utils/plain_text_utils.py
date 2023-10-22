import re
import textwrap

from src.log_config_loader import log

tabwidth = "    "


def fold_text(text: str) -> str:
    # Replace multiple whitespaces with a single space and trim leading/trailing whitespaces
    folded = ' '.join(text.split())
    folded = ' '.join(folded.split("\n"))
    log.debug(f"Folded text {folded}")
    return folded


def replace_n_sym_with_newline(text: str):
    # Ensure that no extra newlines present
    folded = fold_text(text)
    replaced, count = folded.replace("\\n", "\n"), folded.count("\\n")
    log.debug(f'Number of "\\n" replaced with newline: {count}')
    log.debug(f"Replaced text {replaced}")
    return replaced


def replace_new_line_with_n_sym(text: str):
    count = text.count("\n")
    replaced = text.replace("\n", "\\n")
    log.debug(f'Number of newline replaced with "\\n": {count}')
    return replaced


def format_text_entry(text, indent_level):
    # Step 1: Collapse the text into one line
    text = ' '.join(text.split())

    # Step 2: Place line breaks before \n
    text = text.replace('\\n', '\n\\n')

    # Step 4: Wrap lines by word if longer than 85 char without inserting \n symbol
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        wrapped_line = textwrap.fill(line, width=85, expand_tabs=False, replace_whitespace=False)
        for sub_line in wrapped_line.split("\n"):
            wrapped_lines.append(sub_line)

    # Step 3: Indent everything according to the position of the <text> tag
    indented_lines = [indent_level + line for line in wrapped_lines]

    # Remove 2 characters so '\n' is not at the same level as other text
    for i in range(0, len(indented_lines)):
        if "\\n" in indented_lines[i]:
            indented_lines[i] = indented_lines[i][2:]

    return '\n' + '\n'.join(indented_lines) + '\n' + (" " * 8)


def guard_colors(text):
    # Replace named colors e.g. %c[d_green] -> <d_green_color>
    text = re.sub(r'%c\[([a-zA-Z_0-9]+)]', r'<\1_color>', text)

    # Replace numeric colors e.g. %c[0,255,255,255] -> <0_255_255_255_color_num>
    text = re.sub(r'%c\[(\d+,\d+,\d+,\d+)]', lambda m: '<' + m.group(1).replace(',', '_') + '_color_num>', text)

    # Handle the dot pattern
    text = re.sub(r'(<[^>]+_color(?:_num)?)> •', r'\1_dot>', text)

    return text


def unguard_colors(text):
    # Handle the dot pattern first
    text = re.sub(r'(<[^>]+_color(?:_num)?)_dot>', r'\1> •', text)

    # Convert back named colors
    text = re.sub(r'<([a-zA-Z_]+)_color>', r'%c[\1]', text)

    # Convert back numeric colors
    text = re.sub(r'<(\d+_\d+_\d+_\d+)_color_num>', lambda m: '%c[' + m.group(1).replace('_', ',') + ']', text)

    return text

def guard_placeholders(text):
    # Guard actions
    text = re.sub(r'\$\$([A-Z_]+)\$\$', r'<\1_action>', text)

    # Guard variables
    text = re.sub(r'\$([a-z_]+)', r'<\1_var>', text)

    # Guard '%s'
    text = text.replace('%s', '<s_placeholder>')

    # Special case for '%c' that are not followed by '['
    text = re.sub(r'%c(?! ?\[)', '<c_placeholder>', text)

    return text


def unguard_placeholders(text):
    # Unguard actions
    text = re.sub(r'<([A-Z_]+)_action>', r'$$\1$$', text)

    # Unguard variables
    text = re.sub(r'<([a-z_]+)_var>', r'$\1', text)

    # Unguard '%s'
    text = text.replace('<s_placeholder>', '%s')

    # Unguard '%c'
    text = text.replace('<c_placeholder>', '%c')

    return text
