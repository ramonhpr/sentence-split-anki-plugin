from .translator import Translator, JishoTranslator, GoogleTranslator
from .phrase_formatter import JapanesePhraseFormatter, LanguagePhraseFormatter, PhraseFormatter
from .splitter import Splitter, JapaneseSplitter, WhiteSpaceSplitter
from os.path import exists, isdir
import pytest


class MockTranslator(Translator):
    called = False

    def translate(self, text: str):
        self.called = True
        return f'translated {text}'

    @staticmethod
    def name() -> str:
        return 'Mock Translator'


class MockSplitter(Splitter):
    called = False

    def split(self, phrase: str):
        self.called = True
        return phrase.split()


def test_interface():
    try:
        PhraseFormatter(MockTranslator('en', 'pt'), MockSplitter()).format('test')
        assert False
    except TypeError:
        assert True


def test_format():
    translator = MockTranslator('en', 'pt')
    splitter = MockSplitter()
    f = JapanesePhraseFormatter(translator, splitter)
    word = {'orig': 'bla', 'hira': 'blabla'}
    output = f.format(word)
    assert translator.called
    assert output == f'{word["orig"]} ({word["hira"]}) = translated {word["orig"]}\n'

@pytest.mark.parametrize(
    'input,expected',
    [
        ('english test\n\nanother test',
         (('english test', 'english = translated english\ntest = translated test\n\nteste de inglês'),
          ('another test', 'another = translated another\ntest = translated test\n\noutro teste')),)
    ]
)
def test_run(input, expected):
    translator = MockTranslator('en', 'pt')
    splitter = MockSplitter()
    f = LanguagePhraseFormatter(translator, splitter)
    assert f.temp_dir == ''
    output = [(i, j) for i, j in f.run(input)]
    assert f.temp_dir != ''
    assert not exists(f.temp_dir)  # the property remains but the directory should be deleted
    assert translator.called
    assert splitter.called
    assert len(output) == 2
    for i, j in zip(output, expected):
        phrase, translation = i
        print(j)
        expected_phrase, expected_translation = j

        assert phrase == expected_phrase
        assert translation == expected_translation


def test_correct_instance():
    f = JapanesePhraseFormatter()
    assert isinstance(f.translator, JishoTranslator)
    assert isinstance(f.splitter, JapaneseSplitter)
    f = LanguagePhraseFormatter(GoogleTranslator('fr', 'en'))
    assert isinstance(f.translator, GoogleTranslator)
    assert isinstance(f.splitter, WhiteSpaceSplitter)


def test_unsupported_language():
    try:
        MockTranslator('Unsupported language', 'en')
        assert False
    except RuntimeError:
        assert True

    try:
        MockTranslator('en', 'Unsupported language')
        assert False
    except RuntimeError:
        assert True
