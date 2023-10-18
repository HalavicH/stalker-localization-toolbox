"""
This script is All in one solution for working with localization of STALKER (X-ray 1.6.2+) games
It's capable of:
- fetching and validating localization text files
- analyzing and fixing encoding
- analyzing pattern misuse
- translating using DeepL
"""

import argparse
from src.log_config_loader import get_main_logger

log = get_main_logger()


def main():
    log.info("Test")
    parser = argparse.ArgumentParser(description='Check encoding of XML files.')
    parser.add_argument('path', help='Path to the XML file or directory containing XML files.')
    args = parser.parse_args()
    # process_files(args.path)
    log.info(args)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(f"Failed to perform actions. Error: {e}")


