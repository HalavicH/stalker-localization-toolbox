import os.path

import gettext

locale_dir = os.path.dirname(__file__) + '/../locale'
# print(locale_dir)
# gettext.bindtextdomain('sltools', __file__ + './../locale')
# gettext.textdomain('sltools')

selected_lang = os.environ.get("LANGUAGE") or "en"
try:
    lang = gettext.translation('sltools', localedir=locale_dir, languages=[selected_lang])
except FileNotFoundError:
    # Init english
    lang = gettext.translation('sltools', localedir=locale_dir, languages=["en"])

lang.install()

_tr = lang.gettext

