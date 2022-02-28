from argparse import ArgumentError
from pydantic import ConfigError
import pykakasi
import sys
import os
import requests
import json
from configparser import ConfigParser
from progress.bar import Bar
from googletrans import Translator
from jisho_api.word import Word
from gtts import gTTS
kks = pykakasi.kakasi()

input_path = sys.argv[1]
ANKI_CONNECT_URL = 'http://localhost:8765'

def is_particle(arg):
    return arg == 'の' or arg == 'は' or arg == 'に' or arg == 'も' or arg == 'で' or arg == 'が'or arg == 'と' or arg == 'ですが' or arg == '\n' or '?' in arg


def get_jisho_definition(word):
    senses =  Word.request(word).data[0]
    ret = set()
    for sense in senses:
        ret.update(sense.english_definitions)
    return ret

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = requests.post(ANKI_CONNECT_URL, requestJson).json()
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def get_list_of_decks():
    return invoke('deckNames')

config = ConfigParser()
config.read('config.cfg')
decks = get_list_of_decks()
if input_path not in decks:
    raise ArgumentError(None, f'There is no deck with name "{input_path}"')
for section in config.sections():
    if section not in decks:
        raise ConfigError(f'There is no deck with name "{section}"')
with open(input_path) as fd:
    deck = input_path
    from_lang = config[deck]['from_lang'] 
    to_lang = config[deck]['to_lang'] 
    text = fd.read()
    entries = text.split('\n\n')
    bar = Bar('Processing', max=len(entries))
    notes = []
    for entry in entries:
        back = ''
        if from_lang == 'ja':
            for i in kks.convert(entry.replace(' ', '')):
                if not is_particle(i['orig']):
                    try:
                        back += (f"{i['orig']} ({i['hira']}) {get_jisho_definition(i['orig'])}\n")
                    except AttributeError:
                        pass
        else:
            back += '\n'.join(entry.split())
            back += '\n'
        gTTS(text=entry, lang=from_lang, slow=False).save(f'/tmp/{entry}.mp3')
        back += Translator().translate(entry, dest=to_lang, src=from_lang).text
        notes.append({
                "deckName": deck,
                "modelName": "Básico",
                "fields": {
                    "Frente": entry,
                    "Verso": back.replace("\n", "<br />")
                },
                "audio": [{
                    "path": os.path.abspath(f'/tmp/{entry}.mp3'),
                    "filename": f"{entry}.mp3",
                    "skipHash": "7e2c2f954ef6051373ba916f000168dc",
                    "fields": [
                        "Verso"
                    ]
                }],
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                    "duplicateScopeOptions": {
                        "deckName": "Default",
                        "checkChildren": False,
                        "checkAllModels": False
                    }
                },
                "tags": [
                    "generated"
                ],
            })
        bar.next()

    print(invoke('addNotes', notes=notes))