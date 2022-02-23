import pykakasi
import sys
from progress.bar import Bar
from translate import Translator
from jisho_api.word import Word
from gtts import gTTS
kks = pykakasi.kakasi()

input_path = sys.argv[1]


def is_particle(arg):
    return arg == 'の' or arg == 'は' or arg == 'に' or arg == 'も' or arg == 'で' or arg == 'が'or arg == 'と' or arg == 'ですが' or arg == '\n' or '?' in arg


def get_jisho_definition(word):
    senses =  Word.request(word).data[0]
    ret = set()
    for sense in senses:
        ret.update(sense.english_definitions)
    return ret

with open(input_path) as fd:
    text = fd.read()
    entries = text.split('===')
    bar = Bar('Processing', max=len(entries))
    for entry in entries:
        from_lang, to_lang, entry = list(filter(len, entry.split('\n')))
        with open(f"{input_path}.out", 'a') as out:
            out.write(f"{entry}\n")
            if from_lang == 'ja':
                for i in kks.convert(entry.replace(' ', '')):
                    if not is_particle(i['orig']):
                        out.write(f"{i['orig']} ({i['hira']}) {get_jisho_definition(i['orig'])}\n")
            else:
                out.write('\n'.join(entry.split()))
                out.write('\n')
            gTTS(text=entry, lang=from_lang, slow=False).save(f'{entry}.mp3')
            out.write(Translator(from_lang=from_lang, to_lang=to_lang).translate(entry))
            out.write('\n===\n')
            bar.next()
    