from .splitter import JapaneseSplitter, WhiteSpaceSplitter, Splitter
import pytest

js = JapaneseSplitter()
wss = WhiteSpaceSplitter()


@pytest.mark.parametrize(
    'splitter,phrase,expected',
    [
        (js, '私は日本人です', [('私', 'わたし'), ('日本人', 'にほんじん')]),
        (js, '日本語版があったらいいな', [('日本語版', 'にほんごばん'), ('があったらいいな', 'があったらいいな')]),
        (js, 'そんなに力強く握ると 割れちゃうよ', [('そんなに', 'そんなに'), ('力強く', 'ちからづよく'), ('握る', 'にぎる'),
                                   ('割れ', 'われ'), ('ちゃうよ', 'ちゃうよ')]),
        (wss, 'This is a test message', ['This', 'is', 'a', 'test', 'message'])
    ]
)
def test_split(splitter, phrase, expected):
    s = splitter.split(phrase)

    assert len(s) == len(expected)

    for i, j in zip(s, expected):
        if isinstance(splitter, JapaneseSplitter):
            orig, hira = j
            assert i['orig'] == orig
            assert i['hira'] == hira
        else:
            assert i == j


def test_interface():
    try:
        Splitter().split('test')
        assert False
    except TypeError:
        assert True

