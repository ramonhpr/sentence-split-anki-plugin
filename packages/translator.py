from dataclasses import dataclass
from jisho_api.word import Word
from abc import ABC, abstractmethod
import sys
import inspect
import googletrans


def is_valid(lang: str) -> bool:
    return lang not in googletrans.LANGUAGES.keys()


@dataclass
class Translator(ABC):
    # TODO: add lang code as abstract method
    from_lang: str
    to_lang: str

    def __post_init__(self):
        if is_valid(self.from_lang):
            raise RuntimeError(f'Language {self.from_lang} not supported')
        if is_valid(self.to_lang):
            raise RuntimeError(f'Language {self.to_lang} not supported')

    @abstractmethod
    def translate(self, text: str):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def name() -> str:
        return ''


@dataclass
class JishoTranslator(Translator):
    from_lang: str = 'ja'
    to_lang: str = 'en'

    def translate(self, text: str):
        try:
            senses = Word.request(text).data[0]
            ret = set()
            for sense in senses:
                ret.update(sense.english_definitions)
            return ', '.join(ret)
        except AttributeError:
            return ''

    @staticmethod
    def name() -> str:
        return 'Jisho'


class GoogleTranslator(Translator):
    def translate(self, text: str):
        return googletrans.Translator().translate(text, dest=self.to_lang, src=self.from_lang).text

    @staticmethod
    def name() -> str:
        return 'Google Translator'


LIST_TRANSLATORS = [obj.name() for _, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isclass(obj) and
                    issubclass(obj, Translator) and obj.name()]
