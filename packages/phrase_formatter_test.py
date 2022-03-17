from .translator import Translator, JishoTranslator, GoogleTranslator
from .phrase_formatter import JapanesePhraseFormatter, LanguagePhraseFormatter, PhraseFormatter
from .splitter import Splitter, JapaneseSplitter, WhiteSpaceSplitter
import tempfile


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


def test_run():
    translator = MockTranslator('en', 'pt')
    splitter = MockSplitter()
    f = LanguagePhraseFormatter(translator, splitter)
    output = [i for i in f.run('english test')]
    assert translator.called
    assert splitter.called
    assert len(output) == 1
    assert output[0] == 'english = translated english\ntest = translated test\n\nteste de inglês'


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
