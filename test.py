from lxml import etree

def to_str(element):
    return etree.tostring(element, pretty_print=True)


def sort_strings_by_id(root, priority_ids=[]):
    # Create a dictionary to store invalid tags/comments
    elem_to_comments = {}

    # Create a list to hold the sorted <string id=""> elements
    sorted_string_elements = []
    priority_string_elements = []

    # Create a list to temporarily store invalid tags/comments
    comments_per_elem = []

    for elem in root:
        if elem.tag == "string" and elem.get("id") is not None:
            string_id = elem.get("id")

            # If it's a <string id=""> element, add it to the list
            if string_id in priority_ids:
                priority_string_elements.append(elem)
            else:
                sorted_string_elements.append(elem)

            # Add the collected invalid tags/comments to the dictionary and clear the list
            if string_id in elem_to_comments:
                elem_to_comments[string_id].extend(comments_per_elem)
            else:
                elem_to_comments[string_id] = comments_per_elem
            comments_per_elem = []
        else:
            # If it's not a <string id=""> element, add it to the comments_per_elem list
            comments_per_elem.append(elem)

    # Sort the elements alphabetically by their "id" attribute (string id)
    sorted_string_elements.sort(key=lambda elem: elem.get("id", ""))
    priority_string_elements.sort(key=lambda elem: elem.get("id", ""))

    # Remove all elements from the root
    root.clear()

    # Add the sorted elements back to the root, preserving comments
    root.append(etree.Comment('=================='))
    root.append(etree.Comment('Duplicated strings'))
    root.append(etree.Comment('=================='))
    populate_elements(elem_to_comments, root, priority_string_elements)
    root.append(etree.Comment('=================='))
    root.append(etree.Comment('Unique strings'))
    root.append(etree.Comment('=================='))
    populate_elements(elem_to_comments, root, sorted_string_elements)


def populate_elements(invalid_elements, root, sorted_elements):
    for elem in sorted_elements:
        # Insert the stored invalid tags/comments before the corresponding <string> element
        string_id = elem.get("id")
        if string_id in invalid_elements:
            for comment in invalid_elements[string_id]:
                print(f"appending {etree.tostring(comment, pretty_print=True)}")
                root.append(comment)
        print(f"appending {etree.tostring(elem, pretty_print=True)}")
        root.append(elem)


# Usage example:
root = etree.fromstring('''
<string_table>
        <string>
            <text>Apple</text>
        </string>
        <!-- Comment 1 -->
        <string id="C">
            <text>Orange</text>
        </string>
        <invalid_tag>Invalid 1</invalid_tag>
        <!-- Comment 2 -->
        <invalid_tag>Invalid 2</invalid_tag>
        <string id="B">
            <text>Banana</text>
        </string>
        <!-- Comment 3 -->
        <string id="A">
            <text>Grape</text>
        </string>
        <string id="D">
            <text>Cherry</text>
        </string>
        <!-- Comment 4 -->
        <string id="F">
            <text>Fig</text>
        </string>
        <invalid_tag>Invalid 3</invalid_tag>
        <string id="E">
            <text>Dragonfruit</text>
        </string>
        <!-- Comment 5 -->
        <string id="G">
            <text>Grapefruit</text>
        </string>
    </string_table>''')

priority_ids = ["B", "C"]

sort_strings_by_id(root, priority_ids)

# Print the modified XML
print(etree.tostring(root, pretty_print=True).decode())
