#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QWidget, QSizePolicy, QHeaderView, QPushButton, QMessageBox
from PyQt5.QtWidgets import QGridLayout, QTableWidget, QTableWidgetItem, QInputDialog, QLineEdit
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
import os
import glob
import datetime
import feature_dnd as dnd


class BackupFile():
    def __init__(self, name, mods, count, time):
        self.name = name
        self.mods = mods
        self.count = count
        self.time = time


class Backups(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ----------------------------------
        self.setWindowTitle('Backups')
        self.setWindowIcon(QIcon('logo.png'))
        self.folder = 'backup'
        # ---central widget----------------
        self.centralwidget = QWidget(self)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.centralwidget.setMinimumSize(QSize(800, 600))
        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # ---table widget-------------------
        self.table = dnd.TableWidgetDragRows()
        self.table.setColumnCount(3)
        self.header = self.table.horizontalHeader()
        self.header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # ---buttons------------------------
        self.make = QPushButton('Make backup', self.centralwidget)
        self.make.setFixedSize(QSize(170, 60))
        self.load = QPushButton('Load from backup', self.centralwidget)
        self.load.setFixedSize(QSize(170, 60))
        self.delete = QPushButton('Remove backup', self.centralwidget)
        self.delete.setFixedSize(QSize(170, 60))
        self.closew = QPushButton('Close', self.centralwidget)
        self.closew.setFixedSize(QSize(170, 60))
        # ---layout-------------------------
        self.gridLayout.addWidget(self.table, 0, 0, 10, 10)
        self.gridLayout.addWidget(self.make, 10, 1, 2, 2)
        self.gridLayout.addWidget(self.load, 10, 3, 2, 2)
        self.gridLayout.addWidget(self.delete, 10, 5, 2, 2)
        self.gridLayout.addWidget(self.closew, 10, 7, 2, 2)
        # ----------------------------------
        self.setCentralWidget(self.centralwidget)
        self.dataDisplay()

    def make_Backup(self, modList):
        name, okPressed = QInputDialog.getText(self, "Get text", "Backup name:", QLineEdit.Normal, "")
        if okPressed and name != '':
            if not os.path.exists(self.folder):
                os.mkdir(self.folder)
            with open('backup/' + name + '.bak', 'w+', encoding='utf-8') as bfile:
                today = datetime.datetime.today()
                bfile.write(name + ' ' + str(len(modList)) + ' ' + today.strftime('%H:%M:%S-%d/%b/%Y') + '\n')
                for mod in modList:
                    bfile.write(mod.modID + ' ' + str(mod.isEnabled) + '\n')
            self.dataDisplay()
        else:
            QMessageBox.about(self, "Warning", "Enter valid name")

    def load_From_Backup(self, modList, name):
        with open('backup/' + name + '.bak', 'r', encoding='utf-8') as bfile:
            data = bfile.readlines()
            modInfo = data[0].split(' ')
            modInfo.pop()
            newModList = []
            for i in range(1, len(data)):
                a = data[i].split(' ')
                for mod in modList:
                    if mod.modID == a[0]:
                        mod.isEnabled = int(a[1])
                        newModList.append(mod)
                        modList.remove(mod)
                        break
            finalModList = modList + newModList
            return finalModList

    def load_Backup_List(self):
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
            return None
        else:
            template = 'backup/*.bak'
            backups = glob.glob(template)
            return backups

    def dataDisplay(self):
        self.backups = self.load_Backup_List()
        self.table.setRowCount(0)
        labels = ['Name', 'Mod count', 'Creation time']  # добавить потом версию игры
        self.table.setHorizontalHeaderLabels(labels)
        for i in range(2):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)
        counter = 0
        if len(self.backups) != 0:
            self.table.setRowCount(len(self.backups))
            for back in self.backups:
                with open(back, 'r', encoding='utf-8') as bfile:
                    data = bfile.readline()
                    modInfo = data.split(' ')
                    # ----------------------------------
                    self.table.setItem(counter, 0, QTableWidgetItem(modInfo[0]))
                    # ----------------------------------
                    self.table.setItem(counter, 1, QTableWidgetItem(modInfo[1]))
                    # ----------------------------------
                    self.table.setItem(counter, 2, QTableWidgetItem(modInfo[2]))
                    # ----------------------------------
                    counter += 1
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
