from pykakasi import kakasi
from abc import ABC, abstractmethod
import re


class Splitter(ABC):
    __separator = '\n\n'

    @staticmethod
    def split_phrases(text: str):
        return text.split(Splitter.__separator)

    @abstractmethod
    def split(self, phrase: str):
        raise NotImplementedError()


def is_not_particle(word):
    particle_list = ['の', 'は', 'に', 'も', 'で', 'が', 'と', 'を', 'ですが', 'です']
    return word not in particle_list


class JapaneseSplitter(Splitter):
    kks = kakasi()

    def split(self, phrase: str):
        return [word for word in self.kks.convert(phrase.replace(' ', '')) if
                is_not_particle(word['orig']) or word == '\n' or '?' in word]


def match_word_pattern(word):
    return re.compile('[A-Za-zÀ-ÿ\']+').match(word)


class WhiteSpaceSplitter(Splitter):
    def split(self, phrase: str):
        return [word for word in phrase.split() if match_word_pattern(word)]
