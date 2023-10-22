from src.commands.common import get_xml_files_and_log, process_files_with_progress
from src.log_config_loader import log
from src.utils.misc import color_lang


def process_file(file_path, results: list, detailed=False):
    stats = {
        "Unknown": 0
    }
    xml_string = read_xml(file_path)

    root = parse_xml_root(xml_string)
    texts = [elem.text for elem in root.xpath('//text') if elem.text and elem.text.strip()]

    if detailed:
        for text in texts:
            try:
                language, probability = detect_language(text)
            except LangDetectException as e:
                log.debug(e, text)
                stats["Unknown"] += 1
                continue

            if stats.get(language) is None:
                stats[language] = 1
            else:
                stats[language] += 1

    all_text = extract_text_from_xml(xml_string)
    try:
        main_lang, _ = detect_language(all_text)
    except LangDetectException as e:
        log.debug("Can't detect language for the whole file. Probably it's empty")
        main_lang = "Unknown"

    results.append((file_path, stats, main_lang))


def translate(args):
    files = get_xml_files_and_log(args.path, f"Translating from '{color_lang(args)}' to '{color_lang(args.to)}'")
    results = []
    process_files_with_progress(files, process_file, results)
    log.info(f"Total processed files: {len(files)}")
    display_report(results)


def display_report(results):
    pass
