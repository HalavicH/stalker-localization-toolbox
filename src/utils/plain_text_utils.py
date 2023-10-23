import re
import textwrap

from colorama import Fore

from src.log_config_loader import log
from collections import Counter

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
    text = re.sub(r'<([a-zA-Z_0-9]+)_color>', r'%c[\1]', text)

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
    text = re.sub(r'<([A-Z_0-9]+)_action>', r'$$\1$$', text)

    # Unguard variables
    text = re.sub(r'<([a-z_0-9]+)_var>', r'$\1', text)

    # Unguard '%s'
    text = text.replace('<s_placeholder>', '%s')

    # Unguard '%c'
    text = text.replace('<c_placeholder>', '%c')

    return text


def remove_colors(text):
    # Replace named colors e.g. %c[d_green] -> <d_green_color>
    text = re.sub(r'%c\[([a-zA-Z_0-9]+)]', '', text)

    # Replace numeric colors e.g. %c[0,255,255,255] -> <0_255_255_255_color_num>
    text = re.sub(r'%c\[(\d+,\d+,\d+,\d+)]', '', text)

    # Handle the dot pattern
    text = re.sub(r'(<[^>]+_color(?:_num)?)> •', '', text)

    return text


def remove_placeholders(text):
    # Guard actions
    text = re.sub(r'\$\$([A-Z_]+)\$\$', r'', text)

    # Guard variables
    text = re.sub(r'\$([a-z_]+)', r'', text)

    # Guard '%s'
    text = text.replace('%s', '')

    # Special case for '%c' that are not followed by '['
    text = re.sub(r'%c(?! ?\[)', '', text)

    return text


def purify_text(text):
    text = fold_text(text)
    text = remove_colors(text)
    return remove_placeholders(text)


# Detect broken placeholders
# Constants for error types
EXTRA_WHITESPACE_BEFORE_BRACKET = 'Extra whitespace before "["'
EXTRA_WHITESPACE_INSIDE_BRACKETS = 'Extra whitespace inside "[]"'
HYPHEN_IN_NAME = 'Hyphen in the name'


# Error fixing functions
def fix_whitespace_before_bracket(text_list, start, end):
    while text_list[start] != '%':
        text_list.pop(start)


def fix_whitespace_inside_brackets(text_list, start, end):
    # Remove spaces after "%c["
    while text_list[start + 3] == ' ':
        text_list.pop(start + 3)
    # Remove spaces before "]"
    while text_list[end - 2] == ' ':
        text_list.pop(end - 2)
        end -= 1


def fix_hyphen_in_name(text_list, start, end):
    for i in range(start, end):
        if text_list[i] == '-':
            text_list[i] = '_'

        # Configuration block: error types, patterns, and fixing functions


ERROR_CONFIG = {
    EXTRA_WHITESPACE_BEFORE_BRACKET: {
        'pattern': r'(\%c\s+\[)',
        'fix': fix_whitespace_before_bracket
    },
    EXTRA_WHITESPACE_INSIDE_BRACKETS: {
        'pattern': r'(\%c\[\s+|\s+\])',
        'fix': fix_whitespace_inside_brackets
    },
    HYPHEN_IN_NAME: {
        'pattern': r'(%c\[[a-z0-9_]*-(?=[a-z0-9_]*\])\])',
        'fix': fix_hyphen_in_name
    }
}

EVERYTHING_NAME = 'Invalid pattern'
EVERYTHING = {
    'pattern': r'(\%c\[[a-z0-9_\-]+\])',
    'fix': fix_hyphen_in_name
}


def color_the_error(snippet, pattern, rich_style=False):
    if rich_style:
        reset = "[/]"
        apply = "[red]"
    else:
        reset = Fore.RESET
        apply = Fore.RED

    for match in re.finditer(pattern, snippet):
        start, end = match.span()
        result = snippet[:end] + reset + snippet[end:]
        result = result[:start] + apply + result[start:]

        # TODO: handle several patterns
        return result


def check_placeholders(text):
    errors = []
    for error_type, config in ERROR_CONFIG.items():
        pattern = config['pattern']
        for match in re.finditer(pattern, text):
            start, end = match.span()
            error_content = match.group(1)

            # Extract snippet for the same line
            line_start = text.rfind('\n', 0, start) + 1
            line_end = text.find('\n', end) if text.find('\n', end) != -1 else len(text)
            snippet = text[line_start:line_end]

            snippet = color_the_error(snippet, pattern, rich_style=True)

            # Compute row and column
            row = text.count('\n', 0, start) + 1
            col = start - line_start + 1

            # Build error object
            error = {
                'position': {'row': row, 'column': col},
                'type': error_type,
                'snippet': snippet,
                'content': error_content
            }
            errors.append(error)
            log.debug(f"Detected: {error}")
    return errors


COLOR = "color"
COLOR_NUM = "color_num"
ACTION = "action"
VARIABLE = "variable"
PERCENT_S = "percent_s"
LONELY_PERCENT_C = "lonely_percent_c"

COMMON_PATERNS = {
    COLOR: r'%c\[([a-zA-Z_0-9]+)]',
    COLOR_NUM: r'%c\[(\d+,\d+,\d+,\d+)]',
    ACTION: r'\$\$([A-Z_]+)\$\$',
    VARIABLE: r'\$([a-z_]+)',
    PERCENT_S: '%s',
    LONELY_PERCENT_C: r'%c(?! ?\[)',
}


def analyze_patterns_in_text(text):
    report = {}
    for pattern_name in COMMON_PATERNS:
        pattern = COMMON_PATERNS[pattern_name]
        all_patterns = re.findall(pattern, text)
        if all_patterns:
            log.debug(all_patterns)

        count_dict = dict(Counter(all_patterns))
        if len(count_dict) > 0:
            report[pattern_name] = count_dict

    return report
