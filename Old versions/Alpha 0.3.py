#!/usr/bin/python3
#-*- coding:utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QAction, QMainWindow, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QDropEvent, QColor, QBrush
import json


LastStateRole = Qt.UserRole

#частично использован код https://github.com/haifengkao/StellairsLoadOrderFixer24/blob/master/load_order_stellaris24.py
# мод и сортировка к нему
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


#таблица и метод для перетаскивания (https://stackoverflow.com/a/43789304/10817033)
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
#конец кода перетаскивания

#главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(900, 600))
        self.setWindowTitle("Отображение данных")
        self.table = TableWidgetDragRows()
        self.table.setColumnCount(5)
        self.setCentralWidget(self.table)
        
        self.modList =[]
        self.getModData('mods_registry.json', 'dlc_load.json')
        
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(sys.exit)
        
        orderAction = QAction('&Sort by alphabetical', self)
        orderAction.setShortcut('Ctrl+W')
        orderAction.triggered.connect(self.sortByType)
        
        dumpAction = QAction('&Save load order', self)
        dumpAction.setShortcut('Ctrl+S')
        dumpAction.triggered.connect(self.dumpLoadOrder)
        
        #добавить сохранение начальных данных и их возвращение
        
        self.menu = self.menuBar()
        prMenu = self.menu.addMenu('&Program')
        prMenu.addAction(exitAction)
        orderMenu = self.menu.addMenu('&Load order')
        orderMenu.addAction(orderAction)
        orderMenu.addAction(dumpAction)  
        
        self.dataDisplay()

    #получение данных из файлов
    def getModData(self, gdata, load):
        with open(gdata, encoding='UTF-8') as gameData:
            data = json.load(gameData)
            self.modList = self.getModList(data)
        with open(load, encoding='UTF-8') as loadOrder:
            order = json.load(loadOrder)
            self.getLoadList(order)
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
                mod = Mod(key, name, steamid, version, source, isEnabled='no')
                self.modList.append(mod)
            except KeyError:
                print('key not found in ', name)
        return self.modList
    
    def getLoadList(self, data):
        load = data['enabled_mods'] 
        for i in load:
            for j in self.modList:
                if str(i) == j.steamid:
                    j.isEnabled = 'yes'
    
    #методы для меню
    def sortByType(self):
        self.modList.sort(key=sortedKey, reverse=True)
        self.dataDisplay()
        
    def dumpLoadOrder(self):
        self.retrieveData()
        #self.writeLoadOrder()
        self.writeDisplayOrder()
    
    #обновление таблицы
    def dataDisplay(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.modList))
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Version", "Source", "Status"])
        for i in range(0, 4):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)
            
        counter = 0
        for mod in self.modList:
            #----------------------------------
            self.table.setItem(counter, 0, QTableWidgetItem(mod.steamid))
            #----------------------------------
            self.table.setItem(counter, 1, QTableWidgetItem(mod.name))
            #----------------------------------
            vs = QTableWidgetItem(mod.version)
            vs.setTextAlignment(Qt.AlignHCenter)
            self.table.setItem(counter, 2, vs)
            #----------------------------------
            src = QTableWidgetItem(mod.source)
            src.setTextAlignment(Qt.AlignHCenter)
            self.table.setItem(counter, 3, src)
            #----------------------------------
            chbx = QTableWidgetItem()
            chbx.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if mod.isEnabled == 'yes':
                chbx.setCheckState(Qt.Checked)
            else:
                chbx.setCheckState(Qt.Unchecked)
            chbx.setData(LastStateRole, chbx.checkState())
            self.table.setItem(counter, 4, chbx)
            #----------------------------------
            if mod.isEnabled == 'yes':
                for i in range(5):
                    self.table.item(counter, i).setBackground(QColor('gray'))
            #----------------------------------
            counter += 1
        
        self.table.cellDoubleClicked.connect(self.onCellChanged)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeColumnsToContents()
    
    def onCellChanged(self, row, column):
        clr = self.modList[row].isEnabled
        if clr == 'no':
            for i in range(5):
                self.table.item(row, i).setBackground(QColor('gray'))
        else:
            for i in range(5):
                self.table.item(row, i).setBackground(QColor('white'))

    def retrieveData(self):
        self.idList = [mod.steamid for mod in self.modList]
        modListNew = []
        for i in range(len(self.modList)):
            item = self.table.item(i, 0)
            ID = item.text()
            r = self.idList.index(ID)
            modListNew.append(self.modList[r])
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
