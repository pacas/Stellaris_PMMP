#!/usr/bin/python3
#-*- coding:utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QAction, QMainWindow, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QDropEvent
import json


# мод и сортировка к нему
def sortedKey(mod):
    return mod.sortedKey

class Mod():
    def __init__(self, hashid, name, steamid, version, source):
        self.hashid = hashid
        self.name = name
        self.steamid = steamid
        self.version = version
        self.source = source
        self.sortedKey = name.encode('utf8', errors='ignore')


#таблица и метод для перетаскивания (найдено в инете)
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

#главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(900, 600))
        self.setWindowTitle("Отображение данных")
        self.table = TableWidgetDragRows()
        self.table.setColumnCount(4)
        self.setCentralWidget(self.table)
        
        self.modList =[]
        self.getModData('mods_registry.json')
        
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(sys.exit)
        
        orderAction = QAction('&Sort by alphabetical', self)
        orderAction.setShortcut('Ctrl+W')
        orderAction.triggered.connect(self.sortByType)
        
        bumpAction = QAction('&Save load order', self)
        bumpAction.setShortcut('Ctrl+S')
        bumpAction.triggered.connect(self.bumpLoadOrder)
        
        self.menu = self.menuBar()
        prMenu = self.menu.addMenu('&Program')
        prMenu.addAction(exitAction)
        orderMenu = self.menu.addMenu('&Load order')
        orderMenu.addAction(orderAction)
        orderMenu.addAction(bumpAction)
        
        
        self.dataDisplay()
        

    #получение данных из файлов
    def getModData(self, file):
        with open(file, encoding='UTF-8') as json_file:
            data = json.load(json_file)
            self.modList = self.getModList(data)
        if len(self.modList) <= 0:
            print('no mod found')
        self.idList = [mod.steamid for mod in self.modList]
        self.hashList = [mod.hashid for mod in self.modList]

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
                    print('version not found in ', name)
                mod = Mod(key, name, steamid, version, source)
                self.modList.append(mod)
            except KeyError:
                print('key not found in ', name)
        return self.modList
    
    #методы для меню
    def sortByType(self):
        self.modList.sort(key=sortedKey, reverse=True)
        self.dataDisplay()
        
    def bumpLoadOrder(self):
        self.retrieveData()
        #self.writeLoadOrder()
        self.writeDisplayOrder()
    
    #обновление таблицы
    def dataDisplay(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.modList))
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Version", "Source"])
        for i in range(0, 3):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)
            
        counter = 0
        for mod in self.modList:
            self.table.setItem(counter, 0, QTableWidgetItem(mod.steamid))
            self.table.setItem(counter, 1, QTableWidgetItem(mod.name))
            self.table.setItem(counter, 2, QTableWidgetItem(mod.version))
            self.table.setItem(counter, 3, QTableWidgetItem(mod.source))
            counter += 1

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeColumnsToContents()

    def test(self):
        for i in range(len(self.modList)):
            item = self.table.item(0, i)
            ID = item.text()
            print(ID)

    def retrieveData(self):
        self.idList = [mod.steamid for mod in self.modList]
        #print(self.modList)
        modListNew = []
        for i in range(len(self.modList)):
            item = self.table.item(i, 0)
            ID = item.text()
            r = self.idList.index(ID)
            modListNew.append(self.modList[r])
        #self.modList = modListNew
        self.idList = [mod.steamid for mod in modListNew]
        self.hashList = [mod.hashid for mod in modListNew]

    #запись в файлы
    def writeLoadOrder(self):
        data = {}
        with open('dlc_load.json', 'r+') as json_file:
            data = json.load(json_file)
    
        if len(data) < 1:
            print('dlc_load.json loading failed')
        data['enabled_mods'] = self.idList
    
        with open('dlc_load1.json', 'w') as json_file:
            json.dump(data, json_file)


    def writeDisplayOrder(self):
        data = {}
        with open('game_data.json', 'r+') as json_file:
            data = json.load(json_file)
        if len(data) < 1:
            print('game_data.json loading failed')
        data['modsOrder'] = self.hashList
        with open('game_data1.json', 'w') as json_file:
            json.dump(data, json_file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()    
    sys.exit(app.exec())
