import textwrap

from src.log_config_loader import log


def fold_text(text: str) -> str:
    # Replace multiple whitespaces with a single space and trim leading/trailing whitespaces
    folded = ' '.join(text.split())
    folded = ' '.join(folded.split("\n"))
    return folded


def replace_n_sym_with_newline(text: str):
    # Ensure that no extra newlines present
    folded = fold_text(text)
    replaced, count = folded.replace("\\n", "\n"), folded.count("\\n")
    log.debug(f'Number of "\\n" replaced with newline: {count}')
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

