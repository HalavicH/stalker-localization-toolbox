from lxml import etree

from sltools.log_config_loader import log
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.git_utils import is_allowed_to_continue
from sltools.utils.xml_utils import parse_xml_root, to_utf_string_with_proper_declaration, format_xml_string


def sort_files_with_duplicates(args, is_read_only):
    file_path1 = args.paths[0]
    file_path2 = args.paths[1]
    sort_duplicates_only = args.sort_duplicates_only

    if not is_allowed_to_continue(file_path1, args.allow_no_repo, args.allow_dirty, args.allow_not_tracked):
        return
    if not is_allowed_to_continue(file_path2, args.allow_no_repo, args.allow_dirty, args.allow_not_tracked):
        return

    log.info(f"Sorting files: '{file_path1}' and '{file_path2}'")

    # Parse XML roots for both files
    xml_tree1 = read_xml(file_path1)
    root1 = parse_xml_root(xml_tree1)
    xml_tree2 = read_xml(file_path2)
    root2 = parse_xml_root(xml_tree2)

    duplicates = []
    duplicates = find_common_string_ids(root1, root2)
    log.info(f"Found {len(duplicates.keys())} duplicates")

    sort_and_save_file(duplicates, file_path1, root1, sort_duplicates_only)
    sort_and_save_file(duplicates, file_path2, root2, sort_duplicates_only)


def sort_and_save_file(duplicates, file_path, root, sort_duplicates_only):
    log.info(f"Processing file: '{file_path}'")
    sort_strings_by_id(root, duplicates, sort_duplicates_only)
    # For each file use to save the files
    resulting_xtr = to_utf_string_with_proper_declaration(root)
    formatted_xml_str = format_xml_string(resulting_xtr, file_path)
    save_xml(file_path, formatted_xml_str)
    log.info(f"Done with file: '{file_path}'")


def find_common_string_ids(root1, root2):
    # Get dict of elem.get("id") to elem.find("text").text
    string_ids1 = {elem.get("id"): elem.find("text").text for elem in root1.iter("string")}

    # Get map of elem.get("id") to elem.find("text").text
    string_ids2 = {elem.get("id"): elem.find("text").text for elem in root2.iter("string")}

    # Find common string IDs (duplicates) between the two sets
    common_ids = set(string_ids1.keys()).intersection(string_ids2.keys())

    # Create dict of id to True if they have the same text, else False
    duplicates = {string_id: string_ids1[string_id] == string_ids2[string_id] for string_id in common_ids}

    return duplicates


def sort_strings_by_id(root, duplicates, sort_duplicates_only):
    # Create a dictionary to store invalid tags/comments
    elem_to_comments = {}

    # Create a list to hold the sorted <string id=""> elements
    sorted_string_elements = []
    different_duplicates = []
    identical_duplicates = []

    # Create a list to temporarily store invalid tags/comments
    comments_per_elem = []

    for elem in root:
        if elem.tag == "string" and elem.get("id") is not None:
            string_id = elem.get("id")

            # If it's a <string id=""> element, add it to the list
            if string_id in duplicates.keys():
                if duplicates[string_id] is True:
                    identical_duplicates.append(elem)
                else:
                    different_duplicates.append(elem)
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
    if not sort_duplicates_only:
        log.info("Sorting all entries instead of only duplicates")
        sorted_string_elements.sort(key=lambda elem: elem.get("id", ""))
    different_duplicates.sort(key=lambda elem: elem.get("id", ""))
    identical_duplicates.sort(key=lambda elem: elem.get("id", ""))

    # Remove all elements from the root
    root.clear()

    # Add the sorted elements back to the root, preserving comments
    root.append(etree.Comment('========================================================='))
    root.append(etree.Comment('Identical duplicated strings (safe to delete one of them)'))
    root.append(etree.Comment('========================================================='))
    populate_elements(elem_to_comments, root, identical_duplicates)
    root.append(etree.Comment('=================================================================='))
    root.append(etree.Comment('Duplicated string IDs with different content (requires inspection)'))
    root.append(etree.Comment('=================================================================='))
    populate_elements(elem_to_comments, root, different_duplicates)
    root.append(etree.Comment('==============================='))
    root.append(etree.Comment('Unique string IDs (keeping as is)'))
    root.append(etree.Comment('==============================='))
    populate_elements(elem_to_comments, root, sorted_string_elements)


def populate_elements(invalid_elements, root, sorted_elements):
    for elem in sorted_elements:
        # Insert the stored invalid tags/comments before the corresponding <string> element
        string_id = elem.get("id")
        if string_id in invalid_elements:
            for comment in invalid_elements[string_id]:
                log.debug(f"appending {etree.tostring(comment, pretty_print=True)}")
                root.append(comment)
        log.debug(f"appending {etree.tostring(elem, pretty_print=True)}")
        root.append(elem)
