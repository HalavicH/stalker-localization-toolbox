"""
This script is All in one solution for working with localization of STALKER (X-ray 1.6.2+) games
It's capable of:
- fetching and validating localization text files
- analyzing and fixing encoding
- analyzing pattern misuse
- translating using DeepL
"""

import argparse
import logging

from src.log_config_loader import get_main_logger

log = get_main_logger()


def parse_args():
    parser = argparse.ArgumentParser(description='My App Description')

    subparsers = parser.add_subparsers(dest='command', help='Sub-commands available:')

    # validate-encoding | ve
    parser_ve = subparsers.add_parser('validate-encoding', aliases=['ve'],
                                      help='Validate encoding of a file or directory')
    parser_ve.add_argument('path', help='Path to file or directory')

    # fix-encoding | fe
    parser_fe = subparsers.add_parser('fix-encoding', aliases=['fe'],
                                      help='Fix encoding of a file or directory (Warning: may break encoding if detected wrongly)')
    parser_fe.add_argument('path', help='Path to file or directory')

    # validate-xml | vx
    parser_vx = subparsers.add_parser('validate-xml', aliases=['vx'], help='Validate XML of a file or directory')
    parser_vx.add_argument('path', help='Path to file or directory')

    # format-xml | fx
    parser_fx = subparsers.add_parser('format-xml', aliases=['fx'], help='Format XML of a file or directory')
    parser_fx.add_argument('path', help='Path to file or directory')

    # check-primary-lang | cpl
    parser_cpl = subparsers.add_parser('check-primary-lang', aliases=['cpl'],
                                       help='Check primary language of a file or directory')
    parser_cpl.add_argument('path', help='Path to file or directory')

    # translate | tr
    parser_tr = subparsers.add_parser('translate', aliases=['tr'], help='Translate text in a file or directory')
    parser_tr.add_argument('path', help='Path to file or directory')
    parser_tr.add_argument('--from', dest='from_lang', help='Source language (auto-detect if missing)')
    parser_tr.add_argument('--to', dest='to_lang', required=True, help='Target language')
    parser_tr.add_argument('--api-key', required=True, help='API key for translation service')

    # analyze-patterns | ap
    parser_ap = subparsers.add_parser('analyze-patterns', aliases=['ap'],
                                      help='Analyze patterns in a file or directory')
    parser_ap.add_argument('path', help='Path to file or directory')

    # fix-known-broken-patterns | fbp
    parser_fbp = subparsers.add_parser('fix-known-broken-patterns', aliases=['fbp'],
                                       help='Fix known broken patterns in a file or directory')
    parser_fbp.add_argument('path', help='Path to file or directory')

    # TODO: Change log level with env variable
    # # Global logging level settings
    # log_group = parser.add_mutually_exclusive_group()
    # log_group.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    #                        help='Set log level')
    # log_group.add_argument('--verbose', action='store_true', help='Set log level to DEBUG')

    args = parser.parse_args()
    return args


def main():
    # log.debug("Start")
    args = parse_args()
    # process_files(args.path)
    log.info(args)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(f"Failed to perform actions. Error: {e}")
