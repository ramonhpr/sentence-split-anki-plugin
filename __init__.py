from aqt import QAction, gui_hooks, mw
from aqt.webview import WebContent
from aqt.deckbrowser import DeckBrowserBottomBar
from aqt.overview import OverviewBottomBar
from aqt.toolbar import BottomBar
from aqt.utils import disable_help_button, showText, QTimer, QDialog, QVBoxLayout, QTextOption, showInfo, QApplication, QPlainTextEdit, getText
import click

mywindow = None
# def bla(content: WebContent, context):
#     if isinstance(context, OverviewBottomBar):
#         # open a layout of text area in new window
#         # showInfo(QApplication.clipboard().text())
#         link = mw.overview.bottom.create_link('bla', 'insert many', lambda: showInfo(QApplication.clipboard().text()))
#         mw.overview.bottom.link_handlers
#         mw.overview.bottom.draw()
#         # content.body += mw.button('bla', 'insert many') #'<input type="file" id="myFile" name="filename">'

def click_listenner():
    # showInfo(QApplication.clipboard().text())
    oldClipboard = QApplication.clipboard().text()
    diag, box = showText(oldClipboard, plain_text_edit=True, run=False)
    plainTextWidget: QPlainTextEdit = diag.layout().itemAt(0).widget()
    plainTextWidget.setReadOnly(False)
    import threading
    thread = threading.Thread(target=diag.exec_, daemon=True)
    thread.start()
    import time
    while thread.is_alive():
        time.sleep(0.01)
        if QApplication.clipboard().text() != oldClipboard:
            oldClipboard = QApplication.clipboard().text()
            plainTextWidget.setPlainText(f'{plainTextWidget.toPlainText()}\n\n{QApplication.clipboard().text()}')
        QApplication.processEvents()
    
    alltext = plainTextWidget.toPlainText()
    print(alltext)



def add_link_on_top_toolbar(links, toolbar):
    link = toolbar.create_link('bla', 'insert many', click_listenner)
    links.append(link)
     
# def listenner(handled, message: str, context):
#     if message == 'bla':
#         # wip
#         # showText('mybla', plain_text_edit=False)
#         mywindow = QPlainTextEdit(mw.app.activeWindow() or mw)
#         # mywindow.insertPlainText('balblablbalblabla')
#         # mywindow.move(10,10)
#         # mywindow.resize(400, 200)
#         # import gtts
#         # showInfo('entrou')
#     return handled

# gui_hooks.webview_will_set_content.append(bla)
gui_hooks.top_toolbar_did_init_links.append(add_link_on_top_toolbar)
# gui_hooks.webview_did_receive_js_message.append(listenner)
