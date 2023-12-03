import glob
import os
import re
import sys

# Define a regular expression pattern to match Svelte components
svelte_script_pattern = re.compile(r'<script(.*?)>([\s\S]*?)<\/script>')
svelte_style_pattern = re.compile(r'<style(.*?)>([\s\S]*?)<\/style>')


# Function to reorganize a Svelte component
def reorganize_component(component_path):
    with open(component_path, 'r') as file:
        content = file.read()

    # Find the script and style sections using regex
    script_match = svelte_script_pattern.search(content)
    style_match = svelte_style_pattern.search(content)

    # Initialize sections as empty strings
    script_section = ''
    style_section = ''

    # Extract script and style sections if they exist
    if script_match:
        script_section = f'<script{script_match.group(1)}>{script_match.group(2)}</script>'
    if style_match:
        style_section = f'<style{style_match.group(1)}>{style_match.group(2)}</style>'

    # Remove script and style sections from the content
    content = svelte_script_pattern.sub('', content)
    content = svelte_style_pattern.sub('', content)

    # Strip leading and trailing empty lines from the remaining content
    rest_section = content.strip('\n')

    # Remove previous root comments if present
    rest_section = rest_section.replace('<!-- HTML -->', '')
    rest_section = rest_section.replace('<!-- JS -->', '')
    rest_section = rest_section.replace('<!-- CSS -->', '')

    # Reorganize sections in the desired order
    reorganized_content = f"""<!-- HTML -->
{rest_section.strip()}

<!-- JS -->
{script_section.strip()}

<!-- CSS -->
{style_section.strip()}
"""

    # Write the reorganized content back to the file
    with open(component_path, 'w') as file:
        file.write(reorganized_content)


# Define the directory to search for Svelte components
search_directory = sys.argv[1]

# Recursively search for Svelte components using glob
svelte_files = glob.glob(os.path.join(search_directory, '**/*.svelte'), recursive=True)

# Iterate through Svelte components and reorganize them
for svelte_file in svelte_files:
    print("Processing: " + svelte_file)
    reorganize_component(svelte_file)

print(f'Reorganized {len(svelte_files)} Svelte components.')
