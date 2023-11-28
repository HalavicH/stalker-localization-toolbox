#!/usr/bin/python3

"""
This script is All in one solution for working with localization of STALKER (X-ray 1.6.2+) games
It's capable of:
- fetching and validating localization text files
- analyzing and fixing encoding
- analyzing pattern misuse
- translating using DeepL
"""

import os
import sys
import time
import traceback

from sltools.baseline.command_processor import CommandProcessor
from sltools.baseline.parser_definitions import ExtendedHelpParser, CustomHelpFormatter
from sltools.config_file_manager import file_config
from sltools.log_config_loader import log
from sltools.root_commands.AnalyzePatterns import AnalyzePatterns
from sltools.root_commands.CapitalizeText import CapitalizeText
from sltools.root_commands.CheckPrimaryLanguage import CheckPrimaryLanguage
from sltools.root_commands.Config import Config
from sltools.root_commands.FindStringDuplicates import FindStringDuplicates
from sltools.root_commands.FixEncoding import FixEncoding
from sltools.root_commands.FormatXml import FormatXml
from sltools.root_commands.MO2CommandProcessor import MO2CommandProcessor
from sltools.root_commands.Misc import Misc
from sltools.root_commands.SortFilesWithDuplicates import SortFilesWithDuplicates
from sltools.root_commands.Translate import Translate
from sltools.root_commands.ValidateEncoding import ValidateEncoding
from sltools.root_commands.ValidateXml import ValidateXml
from sltools.root_commands.mo2_commands.VfsCopy import VfsCopy
from sltools.root_commands.mo2_commands.VfsMap import VfsMap
from sltools.utils.colorize import *
from sltools.utils.lang_utils import trn
from sltools.utils.misc import check_for_update


def main():
    start_time = time.process_time()
    try:
        log.debug(trn("Start"))
        parser = ExtendedHelpParser(description=trn("app_description"), formatter_class=CustomHelpFormatter)
        root = CommandProcessor([
            Config(),
            ValidateEncoding(),
            FixEncoding(),
            ValidateXml(),
            FormatXml(),
            CheckPrimaryLanguage(),
            Translate(),
            AnalyzePatterns(),
            CapitalizeText(),
            FindStringDuplicates(),
            SortFilesWithDuplicates(),
            MO2CommandProcessor([
                VfsMap(),
                VfsCopy(),
            ]),
            Misc(),
        ])
        root.setup(parser)

        args = parser.parse_args()
        log.debug(trn("Args: %s") % str(args))

        if args.command is None:
            cmd_name = sys.argv[0].split("/")[-1] + " -h"
            log.always(trn(f"Please provide args. Use {cf_green(cmd_name)} for help"))
            sys.exit()

        root.execute(args)

    except Exception as e:
        show_stack_trace = file_config.general.show_stacktrace or False
        if os.environ.get("PY_ST"):
            show_stack_trace = os.environ.get("PY_ST").lower() == 'true'

        if show_stack_trace:
            log.fatal(trn("Failed to perform actions. Error: %s") % traceback.format_exc())
        else:
            log.fatal(trn("Failed to perform actions. Error: %s") % e)

    end_time = time.process_time()
    elapsed_time = end_time - start_time
    log.always(trn("Done! Total time: %s") % cf_green("%.3fs" % elapsed_time))

    get_console().print(check_for_update())
    sys.exit(0)


if __name__ == '__main__':
    main()
