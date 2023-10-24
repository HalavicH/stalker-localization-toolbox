import os.path

from langdetect import detect_langs

from sltools.utils.plain_text_utils import fold_text

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

t = lang.gettext


def detect_language(text, possible_languages=["uk", "en", "ru", "fr", "es"]):
    detections = detect_langs(fold_text(text))
    for detection in detections:
        lang, confidence = str(detection).split(':')
        if lang in possible_languages:
            return lang, float(confidence)
    return "Unknown", 0.0
