import chardet
import glob
import os

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def convert_encoding(file_path, target_encoding='windows-1251'):
    with open(file_path, 'r', encoding=detect_encoding(file_path)) as file:
        file_contents = file.read()
    with open(file_path, 'w', encoding=target_encoding) as file:
        file.write(file_contents)

def process_files(directory, wrong_encoding_to_fix):
    incorrect_encoding_files = []
    xml_files = glob.glob(f'{directory}/**/**/*.xml', recursive=True)

    for file_path in xml_files:
        print(f"Analyzing file: {file_path}")

        encoding = detect_encoding(file_path)
        if encoding.lower() == wrong_encoding_to_fix:
            incorrect_encoding_files.append((file_path, encoding))

    for file_path, encoding in incorrect_encoding_files:
        print(f"File: {file_path} | Encoding: {encoding}")
        convert_encoding(file_path)

    print(f"Processed {len(incorrect_encoding_files)} files.")

# Replace 'your_directory' with the path to the directory containing your XML files
process_files('.', "utf-8")
