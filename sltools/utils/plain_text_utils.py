import re
import textwrap

from colorama import Fore

from sltools.baseline.config import text_wrap_width
from sltools.log_config_loader import log
from collections import Counter
from sltools.utils.lang_utils import trn

from sltools.utils.colorize import rich_guard

tabwidth = "    "


def fold_text(text: str) -> str:
    # Replace multiple whitespaces with a single space and trim leading/trailing whitespaces
    folded = ' '.join(text.split())
    folded = ' '.join(folded.split("\n"))
    log.debug(trn("Folded text %s") % folded)
    return folded


def replace_n_sym_with_newline(text: str):
    folded = fold_text(text)
    replaced, count = folded.replace("\\n", "\n"), folded.count("\\n")
    log.debug(trn('Number of "\\n" replaced with newline: %s') % count)
    log.debug(trn("Replaced text %s") % replaced)
    return replaced


def replace_new_line_with_n_sym(text: str):
    count = text.count("\n")
    replaced = text.replace("\n", "\\n")
    log.debug(trn('Number of newline replaced with "\\n": %s') % count)
    return replaced


def format_text_entry(text, indent_level):
    # Step 1: Collapse the text into one line
    text = ' '.join(text.split())

    # Step 2: Place line breaks before \n
    text = text.replace('\\n', '\n\\n')

    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        wrapped_line = textwrap.fill(line, width=text_wrap_width, expand_tabs=False, replace_whitespace=False)
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


# Detect broken placeholders
# Constants for error types
EXTRA_WHITESPACE_BEFORE_BRACKET = 'Extra whitespace before "["'
EXTRA_WHITESPACE_INSIDE_BRACKETS = 'Extra whitespace inside "[]"'
HYPHEN_IN_NAME = 'Hyphen in the name'
NAME_STARTS_WITH_NUMBER = 'Placeholder name starts with number'
# Configuration block: error types, patterns, and fixing functions
ERROR_CONFIG = {
    EXTRA_WHITESPACE_BEFORE_BRACKET: {
        'pattern': r'(\%c\s+\[[a-z0-9_\-]+\])',
        'fix': 'fix_whitespace_before_bracket'  # Placeholder function name
    },
    EXTRA_WHITESPACE_INSIDE_BRACKETS: {
        'pattern': r'(\%c\[\s+[a-z0-9_\-]+\]|\%c\[[a-z0-9_\-]+\s+\])',
        'fix': 'fix_whitespace_inside_brackets'  # Placeholder function name
    },
    HYPHEN_IN_NAME: {
        'pattern': r'(%c\[[a-z0-9_]+-(?=[a-z0-9_]*\]))',
        'fix': 'fix_hyphen_in_name'  # Placeholder function name
    },
    NAME_STARTS_WITH_NUMBER: {
        'pattern': r'(%c\[\d+[a-z0-9_\-]*\])',
        'fix': 'fix_name_starts_with_number'  # Placeholder function name
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
        before_start = rich_guard(snippet[:start])
        after_start = snippet[start:]
        after_start_before_end = rich_guard(after_start[:(end - start)])
        after_start_after_end = rich_guard(after_start[(end - start):])

        result = before_start + apply + after_start_before_end + reset + after_start_after_end

        # TODO: handle several patterns
        return result


def check_placeholders(text, xml_string):
    errors = []
    for error_type, config in ERROR_CONFIG.items():
        pattern = config['pattern']
        for match in re.finditer(pattern, text):
            start, end = match.span()
            error_content = match.group(1)

            # Compute global position in xml_string
            global_start = xml_string.find(text) + start
            global_end = xml_string.find(text) + end

            # Extract snippet for the same line
            line_start_global = xml_string.rfind('\n', 0, global_start) + 1
            line_end_global = xml_string.find('\n', global_end) if xml_string.find('\n', global_end) != -1 else len(
                xml_string)
            snippet = xml_string[line_start_global:line_end_global]
            snippet = color_the_error(snippet, pattern, True)

            # Compute row and column
            row = xml_string.count('\n', 0, global_start) + 1
            col = global_start - line_start_global + int(len(error_content) / 2)

            # Enhance snippet to show a few lines before and after the error and point out the exact error position
            prev_line_start = xml_string.rfind('\n', 0, line_start_global - 1) + 1

            if xml_string.find('\n', line_end_global + 1) != -1:
                next_line_end = xml_string.find('\n', line_end_global + 1)
            else:
                next_line_end = len(xml_string)

            prev_line = rich_guard(xml_string[prev_line_start:line_start_global].rstrip())
            next_line = rich_guard(xml_string[line_end_global + 1:next_line_end].rstrip())

            arrow_line = len(str(row)) * ' ' + ' ' * (col - 1) + '-^-'
            enhanced_snippet = f"{row - 1}: {prev_line}\n{row}: {snippet}\n{arrow_line}\n{row + 1}: {next_line}"

            # Build error object
            error = {
                'position': {'row': row, 'column': col},
                'type': error_type,
                'snippet': enhanced_snippet,
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
    COLOR: r'(%c\[[a-zA-Z_0-9]+\])',
    COLOR_NUM: r'(%c\[\d+,\d+,\d+,\d+\])',
    ACTION: r'(\$\$[A-Z_0-9]+\$\$)',
    VARIABLE: r'(\$[a-z_0-9]+)',
    PERCENT_S: '%s',
    LONELY_PERCENT_C: r'(%c?! ?\[)',
}


def analyze_patterns_in_text(text):
    report = {}
    for pattern_name in COMMON_PATERNS:
        pattern = COMMON_PATERNS[pattern_name]
        all_matches = re.findall(pattern, text)
        for i, match in enumerate(all_matches):
            all_matches[i] = rich_guard(match)

        if all_matches:
            log.debug(trn("Pattern matches: %s") % all_matches)

        count_dict = dict(Counter(all_matches))
        if len(count_dict) > 0:
            report[pattern_name] = count_dict

    return report
