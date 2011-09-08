#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from binascii import crc32
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
from PyQt4 import QtCore, QtGui
from PyQt4 import QtNetwork  # for py2exe

import filepad
import utils
if len(sys.argv) == 2 and sys.argv[1] == 'update_ui':
    # recompile ui
    for filename in ['mainform', 'add_pad', 'settings', 'sync']:
        os.system('pyuic4 -o ui/%s.py ui/%s.ui' % (filename, filename))
        os.system('pyrcc4 -o ui/resources_rc.py ui/resources.qrc')
import ui


DIR_EXISTS_MSG = u'Там, куда вы передвигаете страницу, уже существует страница с таким же slug. Поменяйте slug одной из страниц.'
CSS = '''<style type="text/css">
h1, h2, h3, h4, h5, h6, npre, blockquote, ul, ol, dl {margin: 20px 0;}  
h1 {font-size: 130%; margin-top: 10px;}
h2 {font-size: 120%; margin-top: 25px;}
h3 {font-size: 110%;}
pre {white-space: pre;}
pre code {background: #f8fff8; display: block; padding: 5px; border: 1px solid #ded; border-left: 3px solid #ded;}
table {border-collapse: collapse; font-size: 100%;}
td, th {padding: 5px 10px;}
th {text-align: center; font-weight: bold; border: 1px solid gray;}
td {text-align: left; border: 1px dashed gray;}
</style>'''
INTRO_PAGE = '''
Добро пожаловать в ZenPad
=========================

- документация по блокноту доступна по адресу: <http://about.zenpad.ru/>
- задать вопрос или сообщить об ошибке можно в группе: <http://groups.google.com/group/zenpad>

Приятной работы :)'''.strip()


class PageTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, page):
        super(QtGui.QTreeWidgetItem, self).__init__([page.title])
        self.page_slug = page.slug
    
    @property
    def page_path(self):
        items = [self]
        while True:
            parent = items[0].parent()
            if not parent:
                break
            items.insert(0, parent)
        return filepad.Page.path_as_str([item.page_slug for item in items])


class MainForm(QtGui.QMainWindow, ui.mainform.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.setupUi(self)
        self.showMaximized()
        
        self.textEdit = TextEdit(self.text_tab)
        self.textEdit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_3.addWidget(self.textEdit, 0, 0, 1, 1)
        self.slugEdit.setValidator(QtGui.QRegExpValidator(
            QtCore.QRegExp('([0-9A-Za-z\-])+'), self.slugEdit))
        # hide QDockWidget title
        self.dockWidget.setTitleBarWidget(QtGui.QWidget())

        self.connect(self.tree,
            QtCore.SIGNAL('itemClicked (QTreeWidgetItem *,int)'), self.treeClick)
        self.connect(self.textEdit,
            QtCore.SIGNAL('textChanged ()'), self.textChanged)
        self.connect(self.tabWidget,
            QtCore.SIGNAL('currentChanged (int)'), self.tabChanged)
        self.connect(self.padList,
            QtCore.SIGNAL('activated (const QString&)'), self.padChanged)
        self.connect(self.slugEdit,
            QtCore.SIGNAL('editingFinished ()'), self.slugChanged)
            
        self.init_pad()
        
    def init_pad(self, pad_name=None):
        pad = filepad.FilePad()
        name_list = pad.all_pads_names()
        if not name_list:
            os.makedirs(os.path.join(filepad.PADS_DIR, 'first'))
            open(os.path.join(
                filepad.PADS_DIR, 'first.txt'), 'w').write(INTRO_PAGE)
            name_list.append('first')
        cfg = filepad.FilePad.load_pads_config()
        pad_name = pad_name or cfg.get('__last_used__')
        if pad_name not in name_list:
            pad_name = name_list[0]
        self.padList.clear()
        self.padList.addItems(name_list)
        self.padList.setCurrentIndex(name_list.index(pad_name))
        self.tree.clear()
        self.pad = filepad.FilePad(pad_name)
        last_path = cfg.get(pad_name, {}).get('last_page', '/')
        try:
            cur_page = self.pad.load_page(last_path)
        except filepad.PageNotFound:
            cur_page = self.pad.load_page('/')
        self.load_tree(cur_page.path)
        self.page = None
        self.load_page(cur_page.path)
        active_tab = cfg.get(pad_name, {}).get('active_tab', 1)
        self.tabWidget.setCurrentIndex(active_tab)


    def load_tree(self, cur_page_path):
        root = self.pad.load_page('/')
        item = PageTreeItem(root)
        self.tree.addTopLevelItem(item)
        if cur_page_path == '/':
            self.tree.setCurrentItem(item)
            self.tree.expandItem(item)
        self._load_tree_rec(cur_page_path, root, item)
    
    def _load_tree_rec(self, cur_page_path, parent, parent_item):
        for child in parent.get_childs():
            item = PageTreeItem(child)
            parent_item.addChild(item)
            if item.page_path == cur_page_path:
                self.tree.setCurrentItem(item)
                self.tree.expandItem(item)
            self._load_tree_rec(cur_page_path, child, item)

    def load_page(self, path):
        self.save_cur_page()
        self.page = self.pad.load_page(path)
        self.page.menu_item = self.tree.currentItem()
        self.textEdit.setPlainText(self.page.content)
        self.slugEdit.setText(self.page.basename)
        if self.page.path == '/':
            self.slugLabel.setText(u'Папка блокнота:')
        else:
            self.slugLabel.setText(u'Slug:')
        if self.tabWidget.currentIndex() == 0:
            self.textEdit.setFocus()
        self._update_html()
        self.actionSave.setDisabled(True)
        self._set_button_status()
        self._update_last_used_page()
    
    def _update_last_used_page(self):
        cfg = self.pad.load_pads_config()
        pad_cfg = cfg.setdefault(self.pad.name, {})
        pad_cfg['last_page'] = self.page.path
        cfg.save()
    
    def _update_html(self):
        self.page.content = unicode(self.textEdit.toPlainText())
        if self.tabWidget.currentIndex() == 1:
            self.webView.setHtml( 
                CSS + self.page.content_html(self.pad.html_converter))
        elif self.tabWidget.currentIndex() == 2:
            self.htmlSource.setPlainText(
                self.page.content_html(self.pad.html_converter))
        
    def _set_button_status(self):
        parent = self.page.menu_item.parent()
        index = parent.indexOfChild(self.page.menu_item) if parent else -1
        if parent:
            self.actionAddSibling.setEnabled(True)
            if index:
                self.actionMoveUp.setEnabled(True)
            else:
                self.actionMoveUp.setDisabled(True)
            if index + 1 < parent.childCount():
                self.actionMoveDown.setEnabled(True)
            else:
                self.actionMoveDown.setDisabled(True)
            if parent.parent():
                self.actionMoveLeft.setEnabled(True)
            else:
                self.actionMoveLeft.setDisabled(True)
            if index:
                self.actionMoveRight.setEnabled(True)
            else:
                self.actionMoveRight.setDisabled(True)
        else:
            self.actionMoveUp.setDisabled(True)
            self.actionMoveDown.setDisabled(True)
            self.actionMoveLeft.setDisabled(True)
            self.actionMoveRight.setDisabled(True)
            self.actionAddSibling.setDisabled(True)
    
    def save_cur_page(self):
        if self.page and self.actionSave.isEnabled():
            self.page.content = unicode(self.textEdit.toPlainText())
            self.page.save()
            old_dir = unicode(self.slugEdit.text())
            if old_dir.startswith(filepad.AUTO_SLUG):
                # basename may be changed
                self.page.menu_item.page_slug = self.page.slug
                self.slugEdit.setText(self.page.basename)
                self._update_last_used_page()
            self.actionSave.setDisabled(True)
            self.page.menu_item.setData(
                0, QtCore.Qt.DisplayRole, QtCore.QVariant(self.page.title))
    
    def treeClick(self, item, column):
        self.load_page(item.page_path)

    def textChanged(self):
        if self.page:
            content = unicode(self.textEdit.toPlainText())
            if self.page.content != content:
                self.actionSave.setEnabled(True)
            title = content.lstrip(' #\n\r\t').split('\n', 1)[0].rstrip()
            title = title or self.page.basename
            if unicode(self.page.menu_item.text(0)) != title:
                self.page.menu_item.setText(0, title)

    def tabChanged(self, tab_id):
        if tab_id == 0:
            self.textEdit.setFocus()
        else:
            self._update_html()
        cfg = filepad.FilePad.load_pads_config()
        cfg.setdefault(self.pad.name, {})['active_tab'] = tab_id
        cfg.save()
    
    def padChanged(self, pad_name):
        self.save_cur_page()
        pad_name = unicode(pad_name)
        self.init_pad(pad_name)

    def slugChanged(self):
        slug = unicode(self.slugEdit.text())
        if self.page.path == '/' and self.pad.basename != slug:
            # change pad name
            self.save_cur_page()
            try:
                self.pad.change_basename(slug)
            except filepad.DirExists:
                self.slugEdit.setText(self.pad.name)
                QtGui.QMessageBox.critical(self, u'Ошибка',
                    u'Блокнот с таким именем уже существует',
                QtGui.QMessageBox.Yes)
            else:
                self.init_pad(slug)
        elif self.page.basename != slug:
            # change page slug
            self.save_cur_page()
            try:
                self.page.change_basename(slug)
            except filepad.DirExists:
                self.slugEdit.setText(self.page.basename)
                QtGui.QMessageBox.critical(self, u'Ошибка',
                    u'Такой slug уже существует в этой папке',
                    QtGui.QMessageBox.Yes)
            else:
                self.page.menu_item.page_slug = self.page.slug
                self.page.menu_item.setData(
                    0, QtCore.Qt.DisplayRole, QtCore.QVariant(self.page.title))
                self._update_last_used_page()

    def on_actionCopyUrl_triggered(self, checked=None):
        if checked is not None:
            cfg = self.pad.load_pads_config()
            host = cfg.get(self.pad.name, {}).get('host')
            if not host:
                QtGui.QMessageBox.critical(self, u'Синхронизация не настроена',
                    u'Невозможно сгенерировать url. Укажите домен в настройках синхронизации.',
                    QtGui.QMessageBox.Ok)
                return
            url = u'http://%s%s' % (host, self.page.path)
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(url)

    def on_actionSave_triggered(self, checked=None):
        if checked is not None:
            self.save_cur_page()

    def on_actionAddChild_triggered(self, checked=None):
        if checked is None: return
        self.save_cur_page()
        page = self.pad.create_auto_child_page(self.page)
        page.save()
        self.tree.expandItem(self.tree.currentItem())
        menu_item = PageTreeItem(page)
        self.tree.currentItem().addChild(menu_item)
        self.tree.setCurrentItem(menu_item)
        self.load_page(page.path)
        self.tabWidget.setCurrentIndex(0)

    def on_actionAddSibling_triggered(self, checked=None):
        if checked is None: return
        self.save_cur_page()
        page = self.pad.create_auto_sibling_page(self.page)
        page.save()
        item = PageTreeItem(page)
        parent = self.tree.currentItem().parent()
        index = parent.indexOfChild(self.page.menu_item) + 1
        parent.insertChild(index, item)
        self.tree.setCurrentItem(item)
        self.load_page(page.path)
        self.tabWidget.setCurrentIndex(0)

    def on_actionMoveLeft_triggered(self, checked=None):
        if checked is None: return
        parent = self.page.menu_item.parent()
        p_parent = parent.parent()
        index = p_parent.indexOfChild(parent) + 1
        try:
            self.page.move_left()
        except filepad.DirExists:
            QtGui.QMessageBox.critical(self, u'Ошибка',
                DIR_EXISTS_MSG, QtGui.QMessageBox.Yes)
            return
        item = parent.takeChild(parent.indexOfChild(self.page.menu_item))
        item.page_slug = self.page.slug
        p_parent.insertChild(index, item)
        self.tree.setCurrentItem(item)
        self._set_button_status()

    def on_actionMoveRight_triggered(self, checked=None):
        if checked is None: return
        parent = self.page.menu_item.parent()
        index = parent.indexOfChild(self.page.menu_item)
        if index:
            try:
                self.page.move_right()
            except filepad.DirExists:
                QtGui.QMessageBox.critical(self, u'Ошибка',
                    DIR_EXISTS_MSG, QtGui.QMessageBox.Yes)
                return
            new_parent = parent.child(index - 1)
            item = parent.takeChild(index)
            item.page_slug = self.page.slug
            new_parent.addChild(item)
            self.tree.setCurrentItem(item)
            self._set_button_status()

    def on_actionMoveUp_triggered(self, checked=None):
        if checked is None: return
        self.page.move_up()
        parent = self.page.menu_item.parent()
        index = parent.indexOfChild(self.page.menu_item)
        item = parent.takeChild(index)
        parent.insertChild(index-1, item)
        self.tree.setCurrentItem(item)
        self._set_button_status()

    def on_actionMoveDown_triggered(self, checked=None):
        if checked is None: return
        self.page.move_down()
        parent = self.page.menu_item.parent()
        index = parent.indexOfChild(self.page.menu_item)
        item = parent.takeChild(index)
        parent.insertChild(index+1, item)
        self.tree.setCurrentItem(item)
        self._set_button_status()

    def on_actionDelete_triggered(self, checked=None):
        if checked is None: return
        if self.page.path == '/':
            # delete pad
            reply = QtGui.QMessageBox.warning(self, u'Удаление блокнота',
                u'Вы собираетесь удалить весь блокнот! Вы уверены?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.pad.delete()
                self.init_pad()
        else:
            # delete page
            if self.page.content.strip() or unicode(self.textEdit.toPlainText()
                    ).strip() or self.page.has_childs():
                reply = QtGui.QMessageBox.question(self, u'Удаление',
                    u'Удалить эту страницу и все вложенные?',
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                if reply != QtGui.QMessageBox.Yes:
                    return
            self.page.delete()
            parent = self.page.menu_item.parent()
            parent.takeChild(parent.indexOfChild(self.page.menu_item))
            self.page = None
            self.load_page(self.tree.currentItem().page_path)

    def closeEvent(self, event):
        #~ reply = QtGui.QMessageBox.question(self, u'Выход',
            #~ u'Хотите выйти?', QtGui.QMessageBox.Yes | 
            #~ QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        #~ if reply != QtGui.QMessageBox.Yes:
            #~ event.ignore()
        self.save_cur_page()
        event.accept()

    def on_actionNewPad_triggered(self, checked=None):
        if checked is None: return
        self.save_cur_page()
        dlg = AddPadForm(self)
        res = dlg.exec_()
        if res:
            os.makedirs(dlg.path)
            self.init_pad(dlg.pad_name)

    def on_actionSettings_triggered(self, checked=None):
        if checked is None: return
        self.save_cur_page()
        SettingsForm(self).exec_()
        self._update_html()

    def on_actionSync_triggered(self, checked=None):
        if checked is None: return
        self.save_cur_page()
        SyncForm(self).exec_()


class SyncForm(QtGui.QDialog, ui.sync.Ui_Dialog):
    STAGES = [
        u'Подготовка',
        u'Удаление страниц',
        u'Обновление страниц',
        u'Сортировка',
    ]
    
    def __init__(self, parent=None):
        super(SyncForm, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.pad = parent.pad
        self.timer_id = self.startTimer(0)
        self.sync_iter = self.sync()
        self.stage.clear()
        self.buttonBox.rejected.connect(self.on_reject)
        self.buttonBox.buttons()[0].setText(u'Отмена')
    
    def on_reject(self):
        self.close()

    def timerEvent(self, event):
        try:
            self.sync_iter.next()
        except StopIteration:
            self.killTimer(self.timer_id)
            self.buttonBox.buttons()[0].setText(
                u'Синхронизация завершена, закрыть окно')
    
    def next_stage(self, skip=False):
        if not hasattr(self, 'stage_id'):
            self.stage_id = 0
        else:
            self.stage_id += 1
        stage = self.STAGES[self.stage_id]
        self.stage.setText(u'Этап %i из %i: %s' % (
            self.stage_id + 1, len(self.STAGES), stage))
        if not skip:
            self.logEdit.appendHtml(u'<h3>%s</h3><br>' % stage)
        self.update()
    
    def log(self, msg):
        self.logEdit.insertPlainText(msg)
        self.update()
    
    def log_ok(self):
        self.log('ok\n')
    
    def set_progress(self, max):
        self.progress.reset()
        self.progress.setRange(1, max)
        self.update()
    
    def inc_progress(self):
        self.progress.setValue(self.progress.value() + 1)
        self.update()
    
    def sync(self):
        self.next_stage()
        html_converter = self.pad.html_converter.encode('utf-8')
        yield
        try:
            self.log(u'Получение списка страниц с сервера ...')
            yield
            web_pages = self.pad.sync_query('/get-page-list/')['pages']
            self.log_ok()
            self.log(u'Подготовка локального списка страниц ... ')
            yield
            loc_pages = self.pad.all_pages()
            loc_paths = [p.path for p in loc_pages]
            self.log_ok()
            self.log(u'Анализ ...\n')
            yield
            to_del = []
            for path, crc, md in web_pages:
                if path not in loc_paths:
                    to_del.append(path)
            to_del.sort()
            to_del.reverse()
            self.log(u'- страниц для удаления: %i\n' % len(to_del))
            yield
            # update list
            to_up = []
            web_pages = dict((path, (crc, md)) for path, crc, md in web_pages)
            self.set_progress(len(loc_pages))
            for page in loc_pages:
                content = open(page.filename).read()
                loc_crc32 = crc32(html_converter + content)
                loc_md5 = md5(html_converter + content).hexdigest()
                if page.path not in web_pages:
                    to_up.append((page.path, loc_crc32, loc_md5))
                else:
                    web_crc32, web_md5 = web_pages.get(page.path)
                    if (loc_crc32, loc_md5) != (web_crc32, web_md5):
                        to_up.append((page.path, loc_crc32, loc_md5))
                self.inc_progress()
                yield
            self.log(u'- страниц для обновления: %i\n' % len(to_up))
            yield
            self.next_stage(not to_del)
            if to_del:
                # delete
                self.set_progress(len(to_del))
                for path in to_del:
                    self.log(u'del: %s ... ' % path)
                    yield
                    self.pad.sync_query('/del/', path=path)
                    self.inc_progress()
                    self.log_ok()
            self.next_stage(not to_up)
            if to_up:
                # update
                converter = self.pad.html_converter
                self.set_progress(len(to_up))
                for path, loc_crc32, loc_md5 in to_up:
                    page = self.pad.load_page(path)
                    self.log(u'up: %s ... ' % path)
                    yield
                    self.pad.sync_query('/up/',
                        path=path,
                        title=page.title.encode('utf-8'),
                        crc32=loc_crc32,
                        md5=loc_md5,
                        content=page.content_html(converter).encode('utf-8'))
                    self.inc_progress()
                    self.log_ok()
            # order
            self.next_stage()
            self.log(u'запрос сортировки с сервера ...')
            yield
            web_paths = self.pad.sync_query('/get-path-list/')['paths']
            self.log_ok()
            if web_paths != loc_paths:
                if set(web_paths) != set(loc_paths):
                    raise filepad.SyncError(
                        u'Ошибка сихрнонизации: обновление не удалось')
                        
                def get_child_slugs(data, path):
                    indent = path.count('/')
                    return [p.rsplit('/', 2)[1] for p in data
                        if p.startswith(path) and p.count('/') - 1 == indent]
                
                self.set_progress(len(loc_paths)) 
                for path in loc_paths:
                    loc_childs = get_child_slugs(loc_paths, path)
                    web_childs = get_child_slugs(web_paths, path)
                    if loc_childs != web_childs:
                        self.log(u'sort: %s ... ' % path)
                        yield
                        self.pad.sync_query('/order/', path=path, 
                            childs='|'.join(loc_childs))
                        self.log_ok()
                    self.inc_progress()
        except filepad.SyncError, ex:
            self.logEdit.appendHtml('<span style="color:red">%s</span>' % ex[0])
        else:
            self.logEdit.appendHtml('<h3 style="color:green">%s</h3>' % 
                u'Синхронизация завершена успешно.')
        self.update()


class SettingsForm(QtGui.QDialog, ui.settings.Ui_Dialog):
    def __init__(self, parent=None):
        super(SettingsForm, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.buttonBox.accepted.connect(self.on_accept)
        self.pad = parent.pad
        cfg = self.pad.load_pads_config()
        pad_cfg = cfg.setdefault(self.pad.name, {})
        self.PadHostEdit.setText(pad_cfg.get('host', ''))
        self.AccessCodeEdit.setText(pad_cfg.get('access_code', ''))
        items = [a for a, b in filepad.HTML_CONVERTERS]
        self.converterSelect.addItems(items)
        self.converterSelect.setCurrentIndex(
            items.index(self.pad.html_converter))

    def on_accept(self):
        cfg = self.pad.load_pads_config()
        pad_cfg = cfg.setdefault(self.pad.name, {})
        pad_cfg['host'] = unicode(self.PadHostEdit.text())
        pad_cfg['access_code'] = unicode(self.AccessCodeEdit.text())
        pad_cfg['converter'] = unicode(self.converterSelect.currentText())
        cfg.save()
        self.done(1)


class AddPadForm(QtGui.QDialog, ui.add_pad.Ui_Dialog):
    def __init__(self, parent=None):
        super(AddPadForm, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.label_root.setText(filepad.PADS_DIR + '/')
        self.lineEdit.setFocus()
        self.buttonBox.accepted.connect(self.on_accept)
        self.lineEdit.setValidator(QtGui.QRegExpValidator(
            QtCore.QRegExp('([0-9A-Za-z\-])+'), self.lineEdit))
        items = [a for a, b in filepad.HTML_CONVERTERS]
        self.converterSelect.addItems(items)

    def on_accept(self):
        self.pad_name = str(self.lineEdit.text())
        if self.pad_name:
            self.path = os.path.join(filepad.PADS_DIR, self.pad_name)
            if os.path.isdir(self.path):
                QtGui.QMessageBox.critical(self.parent, u'Ошибка',
                    u'Папка уже существует.', QtGui.QMessageBox.Yes)
                self.done(0)
            else:
                cfg = filepad.FilePad.load_pads_config()
                pad_cfg = cfg.setdefault(self.pad_name, {})
                pad_cfg['converter'] = unicode(self.converterSelect.currentText())
                cfg.save()
                self.done(1)
        else:
            self.done(0)


class TextEdit(QtGui.QPlainTextEdit):
    '''Editor witch block-indentation and auto-newline-indentaiton'''
    def __init__(self, parent):
        QtGui.QTextEdit.__init__(self, parent)
        font = QtGui.QFont()
        self.setStyleSheet('font: 10pt "DejaVu Sans Mono";')
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Tab:
            self.block_indent()
        elif event.key() == QtCore.Qt.Key_Backtab:
            self.block_unindent()
        elif event.key() == QtCore.Qt.Key_Return:
            self.autoindent_newline()
        else:
            super(TextEdit, self).keyPressEvent(event)

    def autoindent_newline(self):
        tab = '    '
        self.indent_character = ':'

        cursor = self.textCursor()
        text = unicode(cursor.block().text())
        trimmed = text.rstrip()
        current_indent_pos = self._get_indent_position(text)

        cursor.beginEditBlock()

        # Create the new line. There is no need to move to the new block, as
        # the insertBlock will do that automatically
        cursor.insertBlock()

        # Remove any leading whitespace from the current line
        after = unicode(cursor.block().text())
        trimmed_after = after.rstrip()
        pos = after.index(trimmed_after)
        for i in range(pos):
            cursor.deleteChar()

        if self.indent_character and trimmed.endswith(self.indent_character):
            # indent one level
            indent = text[:current_indent_pos] + tab
        else:
            # indent to the same level
            indent = text[:current_indent_pos]
        cursor.insertText(indent)

        cursor.endEditBlock()
        self.ensureCursorVisible()

    def block_indent(self):
        cursor = self.textCursor()

        if not cursor.hasSelection():
            # Insert a tabulator
            self.line_indent(cursor)

        else:
            # Indent every selected line
            sel_blocks = self._get_selected_blocks()

            cursor.clearSelection()
            cursor.beginEditBlock()

            for block in sel_blocks:
                cursor.setPosition(block.position())
                self.line_indent(cursor)

            cursor.endEditBlock()
            self._show_selected_blocks(sel_blocks)

    def block_unindent(self):
        cursor = self.textCursor()

        if not cursor.hasSelection():
            # Unindent current line
            position = cursor.position()
            cursor.beginEditBlock()

            removed = self.line_unindent(cursor)
            position = max(position-removed, 0)

            cursor.endEditBlock()
            cursor.setPosition(position)
            self.setTextCursor(cursor)

        else:
            # Unindent every selected line
            sel_blocks = self._get_selected_blocks()

            cursor.clearSelection()
            cursor.beginEditBlock()

            for block in sel_blocks:
                cursor.setPosition(block.position())
                self.line_unindent(cursor)

            cursor.endEditBlock()
            self._show_selected_blocks(sel_blocks)

    def line_indent(self, cursor):
        tab = '    '
        cursor.insertText(tab)

    def line_unindent(self, cursor):
        """ Unindents the cursor's line. Returns the number of characters 
            removed.
        """
        tab = '    '
        cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
        if unicode(cursor.block().text()).startswith(tab):
            new_text = cursor.block().text()[len(tab):]
            cursor.movePosition(QtGui.QTextCursor.EndOfBlock,
                                QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(new_text)
            return len(tab)
        else:
            return 0

    def _get_indent_position(self, line):
        trimmed = line.lstrip()
        if trimmed:
            return len(line) - len(trimmed)
        else:
            # if line is all spaces, treat it as the indent position
            return len(line)

    def _show_selected_blocks(self, selected_blocks):
        """ Assumes contiguous blocks
        """
        cursor = self.textCursor()
        cursor.clearSelection()
        cursor.setPosition(selected_blocks[0].position())
        cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
        cursor.movePosition(QtGui.QTextCursor.NextBlock, 
                            QtGui.QTextCursor.KeepAnchor, len(selected_blocks))
        cursor.movePosition(QtGui.QTextCursor.EndOfBlock, 
                            QtGui.QTextCursor.KeepAnchor)

        self.setTextCursor(cursor)

    def _get_selected_blocks(self):
        cursor = self.textCursor()
        if cursor.position() > cursor.anchor():
            move_op = QtGui.QTextCursor.PreviousBlock
            start_pos = cursor.anchor()
            end_pos = cursor.position()
        else:
            move_op = QtGui.QTextCursor.NextBlock
            start_pos = cursor.position()
            end_pos = cursor.anchor()

        cursor.setPosition(start_pos)
        cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
        blocks = [cursor.block()]

        while cursor.movePosition(QtGui.QTextCursor.NextBlock):
            block = cursor.block()
            if block.position() < end_pos:
                blocks.append(block)

        return blocks


def main():
    app = QtGui.QApplication(sys.argv)
    form = MainForm()
    form.show()
    app.exec_()
   
 
if __name__ == "__main__":
    main()
