from langdetect import detect_langs

from src.utils.plain_text_utils import fold_text


def detect_language(text, possible_languages=["uk", "en", "ru", "fr", "es"]):
    detections = detect_langs(fold_text(text))
    for detection in detections:
        lang, confidence = str(detection).split(':')
        if lang in possible_languages:
            return lang, float(confidence)
    return "Unknown", 0.0
