#!/usr/bin/python3
#-*- coding:utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QAction, QMainWindow
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QDropEvent, QColor
import json
import os
from shutil import copyfile


LastStateRole = Qt.UserRole

# частично использован код из проекта
# https://github.com/haifengkao/StellairsLoadOrderFixer24
# перепишу чуть позже


def sortedKey(mod):
    return mod.sortedKey


class Mod():
    def __init__(self, hashid, name, steamid, version, source, isEnabled):
        self.hashid = hashid
        self.name = name
        self.steamid = steamid
        self.version = version
        self.source = source
        self.isEnabled = isEnabled
        self.sortedKey = name.encode('utf8', errors='ignore')


# таблица и метод для перетаскивания
# https://stackoverflow.com/a/43789304/10817033
class TableWidgetDragRows(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dropEvent(self, event: QDropEvent):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)

            rows = sorted(set(item.row() for item in self.selectedItems()))
            rows_to_move = [[QTableWidgetItem(self.item(row_index, column_index)) for column_index in range(self.columnCount())]
                            for row_index in rows]
            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1

            for row_index, data in enumerate(rows_to_move):
                row_index += drop_row
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    self.setItem(row_index, column_index, column_data)
            event.accept()
            for row_index in range(len(rows_to_move)):
                self.item(drop_row + row_index, 0).setSelected(True)
                self.item(drop_row + row_index, 1).setSelected(True)
        super().dropEvent(event)

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()

        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        return rect.contains(pos, True) and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()
# конец кода перетаскивания


# главное окно
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(QSize(900, 600))
        self.setWindowTitle("PMM - Pacas Mod Manager")
        self.table = TableWidgetDragRows()
        self.table.setColumnCount(4)
        self.setCentralWidget(self.table)
        self.dlc_load = 'dlc_load.json'
        self.mods_registry = 'mods_registry.json'
        self.game_data = 'game_data.json'
        self.folder = 'backup'
        # ----------------------------------
        self.modList = []
        self.getModData(self.mods_registry, self.dlc_load, self.game_data)
        # ----------------------------------
        self.menu = self.menuBar()
        # ---Program------------------------
        prMenu = self.menu.addMenu('&Program')
        dumpACT = QAction('Save load order', self)
        dumpACT.setShortcut('Ctrl+S')
        dumpACT.triggered.connect(self.dumpLoadOrder)
        prMenu.addAction(dumpACT)
        # ----------------------------------
        backupACT = QAction('Back up settings', self)
        backupACT.triggered.connect(self.makeBackup)
        prMenu.addAction(backupACT)
        # ----------------------------------
        exitACT = QAction('Exit', self)
        exitACT.setShortcut('Ctrl+Q')
        exitACT.triggered.connect(sys.exit)
        prMenu.addAction(exitACT)
        # ---Sorting------------------------
        orderMenu = self.menu.addMenu('&Sorting')
        orderACT = QAction('Sort by alphabetical', self)
        orderACT.triggered.connect(self.sortByType)
        orderMenu.addAction(orderACT)
        # ----------------------------------
        lbACT = QAction('Load from backup', self)
        lbACT.triggered.connect(self.loadFromBackup)
        orderMenu.addAction(lbACT)
        # ----------------------------------
        self.dataDisplay()
        self.table.cellDoubleClicked.connect(self.onCellChanged)

    # получение данных из файлов
    def getModData(self, m, d, g):
        with open(m, encoding='UTF-8') as gameData:
            data = json.load(gameData)
            self.modList = self.getModList(data)
        with open(d, encoding='UTF-8') as loadOrder:
            data = json.load(loadOrder)
            self.getLoadList(data)
        # добавить проверку на первый запуск через  файл настроек
        with open(g, encoding='UTF-8') as dataOrder:
            data = json.load(dataOrder)
            self.modList = self.getDisplayList(data)
        self.idList = [mod.steamid for mod in self.modList]

    def getModList(self, data):
        for key, data in data.items():
            try:
                name = data['displayName']
                steamid = data['gameRegistryId']
                source = data['source']
                try:
                    version = data['requiredVersion']
                except KeyError:
                    version = 'not found'
                mod = Mod(key, name, steamid, version, source, isEnabled='no')
                self.modList.append(mod)
            except KeyError:
                print('key not found in ', name)
        return self.modList

    def getLoadList(self, data):
        load = data['enabled_mods']
        for i in load:
            for j in self.modList:
                if str(i) == j.hashid:
                    j.isEnabled = 'yes'
    
    def getDisplayList(self, data):
        load = data['modsOrder']
        newOrder = []
        for i in load:
            for j in self.modList:
                if str(i) == j.steamid:
                    newOrder.append(j)
                    continue
        return newOrder
    
    # загрузка из бэкапа
    def loadFromBackup(self):
        if os.path.exists(self.folder):
            self.modList = []
            self.getModData(self.mods_registry, 'backup//dlc_load.json', 'backup//game_data.json')
            self.dataDisplay()

    # обновление таблицы
    def dataDisplay(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.modList))
        labels = ["Path", "Name", "Version", "Source"]
        self.table.setHorizontalHeaderLabels(labels)
        for i in range(3):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)

        counter = 0
        for mod in self.modList:
            # ----------------------------------
            self.table.setItem(counter, 0, QTableWidgetItem(mod.steamid))
            # ----------------------------------
            self.table.setItem(counter, 1, QTableWidgetItem(mod.name))
            # ----------------------------------
            vs = QTableWidgetItem(mod.version)
            vs.setTextAlignment(Qt.AlignHCenter)
            self.table.setItem(counter, 2, vs)
            # ----------------------------------
            src = QTableWidgetItem(mod.source)
            src.setTextAlignment(Qt.AlignHCenter)
            self.table.setItem(counter, 3, src)
            # ----------------------------------
            if mod.isEnabled == 'yes':
                for i in range(4):
                    self.table.item(counter, i).setBackground(QColor.fromRgb(191, 245, 189))
            # ----------------------------------
            counter += 1

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeColumnsToContents()

    def onCellChanged(self, row, column):
        self.retrieveData()
        clr = self.modList[row].isEnabled
        if clr == 'no':
            for i in range(4):
                self.table.item(row, i).setBackground(QColor.fromRgb(191, 245, 189))
            self.modList[row].isEnabled = 'yes'
        else:
            for i in range(4):
                self.table.item(row, i).setBackground(QColor('white'))
            self.modList[row].isEnabled = 'no'

    def retrieveData(self):
        modListNew = []
        for i in range(len(self.modList)):
            item = self.table.item(i, 0)
            ID = item.text()
            r = self.idList.index(ID)
            modListNew.append(self.modList[r])
        self.modList = modListNew
        self.idList = [mod.steamid for mod in self.modList]

    # методы для меню
    def sortByType(self):
        self.modList.sort(key=sortedKey, reverse=True)
        self.dataDisplay()

    def dumpLoadOrder(self):
        self.retrieveData()
        self.writeLoadOrder()
        self.writeDisplayOrder()
    
    def makeBackup(self):
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        if os.path.isfile(self.dlc_load):
            copyfile(self.dlc_load, self.folder + '//' + self.dlc_load)
        if os.path.isfile(self.game_data):
            copyfile(self.game_data, self.folder + '//' + self.game_data)

    # запись в файлы
    def writeLoadOrder(self):
        data = {}
        with open(self.dlc_load, 'r+') as json_file:
            data = json.load(json_file)
        summary = []
        for mod in self.modList:
            if mod.isEnabled == 'yes':
                summary.append(mod.hashid)
        data['enabled_mods'] = summary
        with open('dlc_load.json', 'w') as json_file:
            json.dump(data, json_file)

    def writeDisplayOrder(self):
        data = {}
        with open(self.game_data, 'r+') as json_file:
            data = json.load(json_file)
        summary = []
        for mod in self.modList:
            summary.append(mod.steamid)
        data['modsOrder'] = summary
        with open('game_data.json', 'w') as json_file:
            json.dump(data, json_file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
