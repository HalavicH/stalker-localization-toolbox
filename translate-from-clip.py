import googletrans
import requests
import pyperclip
import sys
import pync

from colorama import Fore

API_KEY = 'c31842ed-............-468770f60f2d:fx'


def translate_deepl(text, target_language, src_language=None):
    url = 'https://api-free.deepl.com/v2/translate'
    headers = {
        'Authorization': f'DeepL-Auth-Key {API_KEY}'
    }
    data = {
        'text': text,
        'target_lang': target_language.upper(),
    }
    if src_language:
        data['source_lang'] = src_language.upper()

    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()

    if response.status_code != 200:
        raise Exception(f'Error: {response_json.get("message", "API request failed")}')

    return response_json['translations'][0]['text']


def translate_text_google(text, target_language, src_language="auto"):
    print("Src language: ", src_language)
    translator = googletrans.Translator()
    if src_language is None:
        translation = translator.translate(text, dest=target_language)
    else:
        translation = translator.translate(text, src=src_language, dest=target_language)

    return translation.text


def main():
    source_text = pyperclip.paste()
    if len(sys.argv) == 3:
        target_language = sys.argv[1]
        from_language = sys.argv[2]
    elif len(sys.argv) == 2:
        target_language = sys.argv[1]
        from_language = None
    else:
        print("Provide the dest translation language!")
        return

    text_google = translate_text_google(source_text, target_language, from_language)
    translated_text = translate_deepl(source_text, target_language, from_language)
    pyperclip.copy(translated_text)

    message = ""
    message += "Lang from: %s, Lang to: %s" % (from_language, target_language)
    message += "Original text: %s\n" % source_text
    message += "Translated DeepL: %s\n" % (Fore.CYAN + translated_text + Fore.RESET)
    message += "Translated Google: %s\n" % (Fore.YELLOW + text_google + Fore.RESET)
    print(message)

    message = ""
    message += "Original: %s\n" % source_text
    message += "DeepL: %s\n" % translated_text
    message += "Google: %s\n" % text_google

    pync.notify(
        message=message,
        title='Translation completed',
        subtitle="From: '%s', To: '%s'" % ("auto" if from_language is None else from_language, target_language),
        sound=None
    )


if __name__ == "__main__":
    main()
