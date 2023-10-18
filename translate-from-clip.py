import googletrans
import requests
import pyperclip
import sys

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
    print(response)
    response_json = response.json()

    if response.status_code != 200:
        raise Exception(f'Error: {response_json.get("message", "API request failed")}')

    return response_json['translations'][0]['text']


def translate_text_google(text, target_language, src_language=None):
    translator = googletrans.Translator()
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
        target_language = 'uk'
        from_language = 'ru'

    translated_text = translate_deepl(source_text, target_language, from_language)
    text_google = translate_text_google(source_text, target_language, from_language)
    pyperclip.copy(translated_text)
    print(f'Original text: {source_text}')
    print(f'Original lang: {from_language}')
    print(f'Target lang  : {target_language}')
    print(f'Translated DeepL: ' + Fore.CYAN + translated_text + Fore.RESET)
    print(f'Translated Google: ' + Fore.YELLOW + text_google + Fore.RESET)


if __name__ == "__main__":
    main()
