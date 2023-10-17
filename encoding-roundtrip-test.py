import glob
import codecs

from colorama import Fore


def convert_encoding_roundtrip(file_path):
    # Read the file in Windows-1251 encoding
    with codecs.open(file_path, 'r', encoding='windows-1251') as file:
        content = file.read()

    # Convert to UTF-8 and then back to Windows-1251
    content_utf8 = content.encode('utf-8').decode('utf-8')
    content_roundtrip = content_utf8.encode('windows-1251').decode('windows-1251')
    if content == content_roundtrip:
        print(Fore.GREEN + "Content equal" + Fore.RESET)
    else:
        print(Fore.RED + "Content missmatch!" + Fore.RESET)

    # Write the roundtrip content back to the file
    with codecs.open(file_path, 'w', encoding='windows-1251') as file:
        file.write(content_roundtrip)

def main():
    # Define the directory to search (change this to your directory)
    directory = './**/*.xml'

    # Get the list of all XML files in the specified directory and subdirectories
    xml_files = glob.glob(directory, recursive=True)

    # Perform the encoding roundtrip for each XML file
    for file_path in xml_files:
        convert_encoding_roundtrip(file_path)
        print(f'Processed {file_path}')

if __name__ == "__main__":
    main()
