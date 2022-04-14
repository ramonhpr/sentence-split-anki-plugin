from os.path import join, dirname, abspath
import sys
import threading
import time
from typing import List, Tuple, Union, Dict, Any

from aqt import gui_hooks, mw
from aqt.utils import showText, QApplication, QPlainTextEdit, QComboBox, QHBoxLayout, QLabel, QTextCursor

sys.path.append(join(dirname(abspath(__file__)), 'venv', 'lib', 'python3.8', 'site-packages'))
sys.path.append(join(dirname(abspath(__file__)), 'bundle'))

from .packages.phrase_formatter import *
from .packages.translator import *
from .packages.translator import LIST_TRANSLATORS
import googletrans
import tempfile

phrases_processed = 0


def add_combo_box(layout: QHBoxLayout, items: List[Tuple[str, Union[str, Dict[str, Any], None]]],
                  label_text: str, default_value: str) -> QComboBox:
    label = QLabel()
    label.setText(label_text)
    cb = QComboBox()
    for item, data in items:
        cb.addItem(item, data)
    if default_value:
        cb.setCurrentText(default_value)
    layout.insertWidget(1, label)
    layout.insertWidget(2, cb)
    return cb


def add_combo_box_deck(layout: QHBoxLayout):
    deck = mw.col.decks.current()
    return add_combo_box(layout, [(deck['name'], deck) for deck in mw.col.decks.all()], 'Deck:', deck['name'])


def add_combo_box_translator(layout: QHBoxLayout):
    return add_combo_box(layout, [(i, None) for i in LIST_TRANSLATORS], 'Translator:', 'Jisho')


def add_combo_box_language(layout: QHBoxLayout):
    langs = list(googletrans.LANGCODES.items())
    source_cb = add_combo_box(layout, langs, 'Source:', 'japanese')
    dest_cb = add_combo_box(layout, langs, 'Destination:', 'english')
    return source_cb, dest_cb


def click_listener():
    global phrases_processed
    old_clipboard = QApplication.clipboard().text()
    dialog, box = showText(old_clipboard, plain_text_edit=True, run=False)
    plain_text_widget: QPlainTextEdit = dialog.layout().itemAt(0).widget()
    plain_text_widget.setReadOnly(False)
    source_lang, dest_lang = add_combo_box_language(dialog.layout())
    translator_cb = add_combo_box_translator(dialog.layout())
    deck_cb = add_combo_box_deck(dialog.layout())
    # TODO: add button ok and reject when press close
    thread = threading.Thread(target=dialog.exec_, daemon=True)
    thread.start()
    while thread.is_alive():
        time.sleep(0.01)
        if QApplication.clipboard().text() != old_clipboard:
            old_clipboard = QApplication.clipboard().text()
            if plain_text_widget.toPlainText() == '':
                plain_text_widget.setPlainText(QApplication.clipboard().text())
            else:
                plain_text_widget.setPlainText(
                    f'{plain_text_widget.toPlainText()}\n\n{QApplication.clipboard().text()}'
                )
            plain_text_widget.moveCursor(QTextCursor.End)
        QApplication.processEvents()

    all_text = plain_text_widget.toPlainText()
    from_lang = source_lang.currentData()
    to_lang = dest_lang.currentData()
    text_split = all_text.split('\n\n')

    if len(text_split) == 0 or len(all_text) == 0:
        return
    phrases_processed = 0

    def process_text():
        global phrases_processed
        with tempfile.TemporaryDirectory() as tmp_dir:
            for front in text_split:
                if from_lang == 'ja':
                    formatter = JapanesePhraseFormatter()
                else:
                    formatter = LanguagePhraseFormatter(GoogleTranslator(from_lang, to_lang))
                back = formatter.process_phrase(front, tmp_dir)
                deck = deck_cb.currentData()
                notetype = mw.col.models.by_name("Basic")
                note = mw.col.new_note(notetype)
                note['Front'] = front
                note['Back'] = back.replace('\n', '<br/>')
                media_filename = join(tmp_dir, f'{front.strip()}.mp3')
                sound_name = mw.col.media.add_file(media_filename)
                note['Back'] += u'[sound:{}]'.format(sound_name)
                mw.col.add_note(note, deck['id'])
                phrases_processed = phrases_processed + 1

    thread = threading.Thread(target=process_text, daemon=True)
    thread.start()

    win_progress = mw.progress.start(label=f'Processing 0/{len(text_split)} cards')
    while thread.is_alive():
        time.sleep(0.01)
        win_progress.form.label.setText(f'Processing {phrases_processed}/{len(text_split)}')
        QApplication.processEvents()
    mw.progress.finish()
    mw.overview.refresh()


def add_link_on_top_toolbar(links, toolbar):
    link = toolbar.create_link('AddMany', 'Add many', click_listener)
    links.insert(2, link)


gui_hooks.top_toolbar_did_init_links.append(add_link_on_top_toolbar)
