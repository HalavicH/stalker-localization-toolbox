import os.path

import gettext

from sltools.config_file_manager import file_config

locale_dir = os.path.dirname(__file__) + '/../locale'
# print(locale_dir)
# gettext.bindtextdomain('sltools', __file__ + './../locale')
# gettext.textdomain('sltools')

selected_lang = file_config.general.language

# If the language is not set in the config file, check the environment variable
if os.environ.get("LANGUAGE"):
    selected_lang = os.environ.get("LANGUAGE")

# If the language is still not set, fallback to "en"
if not selected_lang:
    selected_lang = "en"

try:
    lang = gettext.translation('sltools', localedir=locale_dir, languages=[selected_lang])
except FileNotFoundError:
    # Init english
    lang = gettext.translation('sltools', localedir=locale_dir, languages=["en"])

lang.install()

trn = lang.gettext

