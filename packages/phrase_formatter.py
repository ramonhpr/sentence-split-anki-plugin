import tempfile

from .translator import JishoTranslator, GoogleTranslator, Translator
from .splitter import Splitter, JapaneseSplitter, WhiteSpaceSplitter
from gtts import gTTS
from os.path import join
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class PhraseFormatter(ABC):
    translator: Translator
    splitter: Splitter
    _temp_dir: str = field(init=False, repr=False, default='')

    @property
    def temp_dir(self) -> str:
        return self._temp_dir

    @abstractmethod
    def format(self, word) -> str:
        raise NotImplementedError()

    def process_phrase(self, phrase, tts_dir) -> str:
        output = ''
        for word in self.splitter.split(phrase):
            output += self.format(word)
        output += '\n'
        gTTS(text=phrase, lang=self.translator.from_lang, slow=False).save(join(tts_dir, f'{phrase}.mp3'))
        output += GoogleTranslator(self.translator.from_lang, self.translator.to_lang).translate(phrase)
        return output

    def run(self, text: str):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._temp_dir = tmp_dir
            for phrase in Splitter.split_phrases(text):
                yield phrase, self.process_phrase(phrase, tmp_dir)

    def run_file(self, input_file):
        with open(input_file) as fd:
            for processed_phrase in self.run(fd.read()):
                yield processed_phrase


@dataclass
class JapanesePhraseFormatter(PhraseFormatter):
    translator: Translator = JishoTranslator()
    splitter: Splitter = JapaneseSplitter()

    def format(self, word: dict) -> str:
        head_formatting = word['orig'] if word['orig'] == word['hira'] else f"{word['orig']} ({word['hira']})"
        tail_formatting = self.translator.translate(word['orig'])
        return f"{head_formatting} = {tail_formatting}\n"


@dataclass
class LanguagePhraseFormatter(PhraseFormatter):
    translator: Translator
    splitter: Splitter = WhiteSpaceSplitter()

    cache = {}

    def format(self, word: str) -> str:
        if word not in self.cache:
            self.cache[word] = self.translator.translate(word)
        return f'{word} = {self.cache[word]}\n'
