from packages.phrase_formatter import *
from packages.translator import *
import sys

_, from_lang, to_lang, input_phrase = sys.argv

if __name__ == '__main__':
    if from_lang == 'ja':
        formatter = JapanesePhraseFormatter()
    else:
        formatter = LanguagePhraseFormatter(GoogleTranslator(from_lang, to_lang))
    print(formatter.process_phrase(input_phrase))
