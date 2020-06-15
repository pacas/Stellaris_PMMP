#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QAction, QMainWindow, QWidget, QSizePolicy, QLabel, QInputDialog, QLineEdit
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHBoxLayout, QVBoxLayout, QMessageBox
from PyQt5.QtWidgets import QPushButton, QHeaderView, QSpacerItem, QTextBrowser, QMenu
from PyQt5.QtCore import QSize, Qt, QEvent, pyqtSlot
from PyQt5.QtGui import QColor, QPixmap, QFont, QIcon
import os
import webbrowser
import feature_dnd as dnd
import platform
from subprocess import Popen
import logging
from glob import glob
import re
import json
import langSelector as l


def sortedKey(mod):
    return mod.sortedKey

def prior(mod):
    return mod.prior


class Mod():
    def __init__(self, name, path, modID, version, tags, isEnabled, source, prior, picture, modfile):
        self.name = name
        self.path = path
        self.modID = modID
        self.version = version
        self.tags = tags
        self.isEnabled = isEnabled
        self.source = source
        self.prior = prior
        self.picture = picture
        self.modfile = modfile
        self.sortedKey = name.encode('utf8', errors='ignore')


# мод менеджер
class ModManager(QMainWindow):
    def __init__(self, first, conn, cursor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ----------------------------------
        self.conn = conn
        self.cursor = cursor
        self.get_Disk_Links()
        self.modList = list()
        self.steamIcon = QPixmap('steam.png')
        self.localIcon = QPixmap('local.png')
        self.filterList = list()
        if not os.path.exists("logs"):
            os.mkdir("logs")
        self.logs = logging.getLogger("St-PMMP")
        handler = logging.FileHandler(filename="logs/err-mm.log", mode="w")
        self.logs.setLevel(logging.ERROR)
        self.logs.addHandler(handler)
        self.getModInfoFromFiles(first)
        self.getModList()
        self.modListBackup = self.modList
        self.setupUI()

    def setupUI(self):
        self.setMinimumSize(QSize(1200, 700))
        self.setWindowTitle(l.r.manager)
        self.setWindowIcon(QIcon('logo.png'))
        # ---central widget----------------
        self.centralwidget = QWidget(self)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.additionalLayout = QVBoxLayout()
        self.filterLayout = QHBoxLayout()
        self.centralwidget.setMinimumSize(QSize(1200, 700))
        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # ---table widget-------------------
        self.table = dnd.TableWidgetDragRows()
        self.table.setColumnCount(4)
        self.header = self.table.horizontalHeader()
        self.header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setColumnWidth(3, 20)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setMinimumSize(QSize(800, 300))
        self.additionalLayout.addWidget(self.table, 0)
        self.verticalLayout = QVBoxLayout()
        self.dataDisplay(self.modList)
        self.table.cellDoubleClicked.connect(self.modSwitch)
        self.table.cellClicked.connect(self.displayModData)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.generateMenu)
        self.table.viewport().installEventFilter(self)
        self.table.setMouseTracking(True)
        self.current_hover = [0, 0]
        # ---filter-------------------------
        self.filterLabel = QLabel(l.r.search, self.centralwidget)
        self.filterLine = QLineEdit('', self.centralwidget)
        self.filterLine.textChanged.connect(self.on_textChanged)
        self.filterClean = QPushButton(l.r.clean, self.centralwidget)
        self.filterClean.clicked.connect(lambda: self.filterLine.setText(''))
        self.filterClean.setMaximumSize(QSize(75, 30))
        self.additionalLayout.addLayout(self.filterLayout)
        self.filterLayout.addWidget(self.filterLabel, 0)
        self.filterLayout.addWidget(self.filterLine, 1)
        self.filterLayout.addWidget(self.filterClean, 2)
        # ---modname------------------------
        self.modname = QLabel(l.r.modTitle, self.centralwidget)
        self.modname.setMinimumSize(QSize(320, 70))
        newfont = QFont('Times', 18, QFont.Bold)
        self.modname.setFont(newfont)
        self.modname.setWordWrap(True)
        self.modname.setAlignment(Qt.AlignHCenter)
        self.verticalLayout.addWidget(self.modname, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        # ---preview pic--------------------
        self.pic = QLabel()
        self.printModPreview('nologo.png')
        self.verticalLayout.addWidget(self.pic, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.verticalLayout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        # ---mod description----------------
        self.textBrowser = QTextBrowser(self.centralwidget)
        newfont = QFont('Verdana', 13, QFont.Bold)
        self.textBrowser.setFont(newfont)
        self.verticalLayout.addWidget(self.textBrowser, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        # ---link button--------------------
        self.verticalLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.linkButton = QPushButton(l.r.openBrowser, self.centralwidget)
        self.linkButton.setFixedSize(QSize(260, 30))
        self.verticalLayout.addWidget(self.linkButton, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        # -------------
        self.linkSteamButton = QPushButton(l.r.openSteam, self.centralwidget)
        self.linkSteamButton.setFixedSize(QSize(260, 30))
        self.verticalLayout.addWidget(self.linkSteamButton, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.verticalLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        # -------------
        self.exitButton = QPushButton(l.r.exitLabel, self.centralwidget)
        self.exitButton.setFixedSize(QSize(260, 30))
        self.verticalLayout.addWidget(self.exitButton, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.verticalLayout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
        # ---finalizing---------------------
        self.horizontalLayout.addLayout(self.additionalLayout)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.setCentralWidget(self.centralwidget)
        # ---menu---------------------------
        self.menu = self.menuBar()
        prMenu = self.menu.addMenu(l.r.programMenu)
        orderMenu = self.menu.addMenu(l.r.sortingMenu)
        self.foldersMenu = self.menu.addMenu(l.r.foldersMenu)
        backupMenu = self.menu.addMenu(l.r.backupsMenu)
        # ---program------------------------
        dumpACT = QAction(l.r.saveOrder, self)
        dumpACT.setShortcut('Ctrl+S')
        dumpACT.triggered.connect(self.dumpLoadOrder)
        prMenu.addAction(dumpACT)
        # -------------
        reloadMods = QAction(l.r.reloadMods, self)
        reloadMods.setShortcut('Ctrl+S')
        reloadMods.triggered.connect(lambda: self.getModInfoFromFiles(0))
        prMenu.addAction(reloadMods)
        # -------------
        helpACT = QAction(l.r.helpLabel, self)
        helpACT.triggered.connect(self.getHelp)
        prMenu.addAction(helpACT)
        # -------------
        self.exitACT = QAction(l.r.exitLabel, self)
        prMenu.addAction(self.exitACT)
        # ---sorting------------------------
        orderACT = QAction(l.r.sortAsc, self)
        orderACT.triggered.connect(lambda: self.sortByType(True))
        orderMenu.addAction(orderACT)
        # -------------
        order1ACT = QAction(l.r.sortDesc, self)
        order1ACT.triggered.connect(lambda: self.sortByType(False))
        orderMenu.addAction(order1ACT)
        # ---folders------------------------
        gameFolder = QAction(l.r.openGameFolder, self)
        gameFolder.triggered.connect(lambda: self.folders_Opener(self.gamepath))
        self.foldersMenu.addAction(gameFolder)
        # -------------
        docsFolder = QAction(l.r.openGameDocs, self)
        docsFolder.triggered.connect(lambda: self.folders_Opener(self.doc_folder))
        self.foldersMenu.addAction(docsFolder)
        # -------------
        localModsFolder = QAction(l.r.openLocalMods, self)
        localModsFolder.triggered.connect(lambda: self.folders_Opener(self.doc_folder + 'mod/'))
        self.foldersMenu.addAction(localModsFolder)
        # ---backups------------------------
        self.openBackupMenu = QAction(l.r.openBackups, self)
        backupMenu.addAction(self.openBackupMenu)
        # -------------
        reload = QAction(l.r.reloadModlist, self)
        reload.triggered.connect(self.reloadOrder)
        backupMenu.addAction(reload)

# ---------------------установка путей игры и работа с ними---------------------------
    def get_Disk_Links(self):
        self.doc_folder = os.path.join(os.path.expanduser('~'), 'Documents', 'Paradox Interactive', 'Stellaris') + '/'
        self.mod_folder = self.doc_folder + '/mod/'
        self.dlc_load = self.doc_folder + 'dlc_load.json'
        self.mods_registry = self.doc_folder + 'mods_registry.json'
        self.mods_data = self.doc_folder + 'mods_data.json'
        self.game_data = self.doc_folder + 'game_data.json'
        self.url = 'https://steamcommunity.com/sharedfiles/filedetails/?id='
        self.steam_url = 'steam://url/CommunityFilePage/'

    def set_Game_Location(self, path):
        self.gamepath = path
        try:
            self.steam = path[:path.find('steamapps') + 10] + 'workshop/content/281990/'
        except:
            self.steam = ''
        if self.steam != '':
            steamModsFolder = QAction(l.r.openSteamMods, self)
            steamModsFolder.triggered.connect(lambda: self.folders_Opener(self.steam))
            self.foldersMenu.addAction(steamModsFolder)

    def folders_Opener(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            Popen(["open", path])
        else:
            Popen(["xdg-open", path])

# ---------------------загрузка данных модификаций------------------------------------
    # получение данных из файлов .mod
    def getModInfoFromFiles(self, firstLaunch):
        try:
            self.modsToAdd = list()
            self.modsToCheck = list()
            self.newValuesForMods = list()
            self.dotModList = glob(self.mod_folder + '*.mod')
            if firstLaunch == 1:
                prior = 0
                self.cursor.execute("CREATE TABLE IF NOT EXISTS mods (name text, path text, modID text, version text, tags text, state bit, source text, prior int, picture text, modfile text)")
                self.conn.commit()
                for mod in self.dotModList:
                    self.getModData(mod, prior, 0)
                    prior += 1
            else:
                self.cursor.execute("SELECT COUNT (*) FROM mods")
                records = self.cursor.fetchall()
                prior = int(records[0][0])
                self.cursor.execute("SELECT * FROM mods")
                records = self.cursor.fetchall()
                for mod in records:
                    if mod[9] not in self.dotModList:
                        self.cursor.execute("DELETE FROM mods WHERE modfile = '" + mod[9] + "'")
                for mod in self.dotModList:
                    self.cursor.execute("SELECT EXISTS(SELECT name FROM mods WHERE modfile = '" + mod + "')")
                    records = self.cursor.fetchall()
                    if records[0][0] == 0:
                        self.getModData(mod, prior, 0)
                        prior += 1
                    else:
                        self.modsToCheck.append(mod)
                for mod in self.modsToCheck:
                    self.getModData(mod, prior, 1)
            self.cursor.executemany("INSERT INTO mods VALUES (?,?,?,?,?,?,?,?,?,?)", self.modsToAdd)
            self.cursor.executemany("UPDATE mods SET name = ?, version = ?, tags = ?, picture = ? WHERE modID = ?", self.newValuesForMods)
            self.conn.commit()
        except:
            self.logs.error("Unexpected error", exc_info=True)
            
    def getModData(self, mod, prior, update):
        try:
            with open(mod) as file:
                data = file.readlines()
                text = ''
                for i in range(len(data)):
                    text += data[i]
                text.replace('replace_path', ' ')
                name = re.search(r'name=".*"', text)
                name = name.group(0)
                name = name[6:-1]
                path = re.search(r'path=".*"', text)
                try:
                    path = path.group(0)
                    path = path[6:-1]
                except AttributeError:
                    path = ''
                if path == '':
                    path = re.search(r'archive=".*"', text)
                    try:
                        path = path.group(0)
                        path = path[9:-1]
                    except AttributeError:
                        path = ''
                version = re.search(r'supported_version=".*"', text)
                if version is None:
                    version = re.search(r'version=".*"', text)
                    try:
                        version = version.group(0)
                        version = version[9:-1]
                    except AttributeError:
                        version = '---'
                else:
                    version = version.group(0)
                    version = version[19:-1]
                remote_file_id = re.search(r'remote_file_id=".*"', text)
                if remote_file_id is None:
                    if path.find('steamapps') != -1:
                        source = 'steam'
                    else:
                        source = 'local'
                else:
                    source = 'steam'
                try:
                    remote_file_id = remote_file_id.group(0)
                    remote_file_id = remote_file_id[16:-1]
                    modID = remote_file_id
                except AttributeError:
                    try:
                        modID = path.split('mod/')
                        modID = modID[1]
                    except:
                        try:
                            modID = path.split('281990/')
                            modID = modID[1]
                            modID = modID.split('/')
                            modID = modID[0]
                        except:
                            modID = '---'
                picture = re.search(r'picture=".*"', text)
                try:
                    picture = picture.group(0)
                    picture = picture[9:-1]
                except AttributeError:
                    picture = ''
                text = text.replace('\n', '')
                text = text.replace('\t', '')
                tags = re.search(r'tags={".*"}', text)
                try:
                    tags = tags.group(0)
                    tags = tags[7:-2]
                    tags = tags.replace('""','\n')
                    if 'dependencies' in tags:
                        tmp = tags.find('}')
                        tags = tags[:tmp-1]
                except AttributeError:
                    tags = ''
                mods = [name, path, modID, version, tags, 0, source, prior, picture, mod]
                if update == 0:
                    self.modsToAdd.append(mods)
                else:
                    newVal = [name, version, tags, picture, modID]
                    self.newValuesForMods.append(newVal)
        except:
            self.logs.error("Unexpected error", exc_info=True)
            
    # получение итоговых данных
    def getModList(self):
        try:
            self.cursor.execute("SELECT * FROM mods")
            records = self.cursor.fetchall()
            for row in records:
                mod = Mod(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                self.modList.append(mod)
            self.modList.sort(key=prior)
            self.idList = [mod.name for mod in self.modList]
        except:
            self.logs.error("Unexpected error", exc_info=True)

# ----------------------визуальная составляющая--------------------------
    # обновление таблицы
    def dataDisplay(self, modList):
        self.modList = modList
        self.table.setRowCount(0)
        self.table.setRowCount(len(modList))
        labels = [l.r.modIDLabel, l.r.name, l.r.version, l.r.modType]
        self.table.setHorizontalHeaderLabels(labels)
        for i in range(4):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)

        counter = 0
        for mod in modList:
            mod.prior = counter
            # ----------------------------------
            self.table.setItem(counter, 0, QTableWidgetItem(mod.modID))
            # ----------------------------------
            self.table.setItem(counter, 1, QTableWidgetItem(mod.name))
            # ----------------------------------
            vs = QTableWidgetItem(mod.version)
            vs.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table.setItem(counter, 2, vs)
            # ----------------------------------
            image = QTableWidgetItem()
            if mod.source == 'steam':
                image.setData(Qt.DecorationRole, self.steamIcon)
            else:
                image.setData(Qt.DecorationRole, self.localIcon)
            image.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table.setItem(counter, 3, image)
            # ----------------------------------
            if mod.isEnabled == 1:
                for i in range(4):
                    self.table.item(counter, i).setBackground(QColor.fromRgb(191, 245, 189))
            # ----------------------------------
            counter += 1

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

    def printModPreview(self, image):
        if os.path.isfile(image):
            tmp = QPixmap(image)
        else:
            tmp = QPixmap('nologo.png')
        tmp = tmp.scaled(256, 256, Qt.KeepAspectRatio)
        self.pic.setPixmap(tmp)

    def modSwitch(self, row, column):
        try:
            self.retrieveData()
            clr = self.modList[row].isEnabled
            if clr == 0:
                for i in range(4):
                    self.table.item(row, i).setBackground(QColor.fromRgb(191, 245, 189))
                self.modList[row].isEnabled = 1
            else:
                for i in range(4):
                    self.table.item(row, i).setBackground(QColor('white'))
                self.modList[row].isEnabled = 0
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def modSwitchAll(self, tp):
        try:
            self.retrieveData()
            for i in range(len(self.modList)):
                self.modList[i].isEnabled = tp
                if tp == 0:
                    for j in range(4):
                        self.table.item(i, j).setBackground(QColor('white'))
                else:
                    for j in range(4):
                        self.table.item(i, j).setBackground(QColor.fromRgb(191, 245, 189))
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def moveMod(self, row, column, tp):
        try:
            if tp == 0:
                newpos, okPressed = QInputDialog.getText(self, '', l.r.newPos, QLineEdit.Normal, '')
                try:
                    newpos = int(newpos)
                    if okPressed and newpos >= 0 and newpos < len(self.modList):
                        if newpos > row:
                            self.modList.insert(newpos, self.modList[row])
                            self.modList.pop(row)
                        else:
                            self.modList.insert(newpos, self.modList[row])
                            self.modList.pop(row + 1)
                        self.retrieveData()
                        self.dataDisplay(self.modList)
                    else:
                        QMessageBox.about(self, l.r.error, l.r.errorPos)
                except:
                    QMessageBox.about(self, l.r.error, l.r.errorPos)
            elif tp == 1 and row != 0:
                self.modList.insert(0, self.modList[row])
                self.modList.pop(row + 1)
                self.retrieveData()
                self.dataDisplay(self.modList)
            elif tp == 2 and row != len(self.modList):
                self.modList.insert(len(self.modList), self.modList[row])
                self.modList.pop(row)
                self.retrieveData()
                self.dataDisplay(self.modList)
            else:
                pass
        except:
            self.logs.error("Unexpected error", exc_info=True)

    # фильтрация эвентов ПКМ меню
    def eventFilter(self, source, event):
        try:
            if(event.type() == QEvent.MouseButtonPress and event.buttons() == Qt.RightButton and source is self.table.viewport()):
                item = self.table.itemAt(event.pos())
                if item is not None:
                    self.rcmenu = QMenu(self)
                    # -------------------move mod------------------
                    mMod = QAction(l.r.moveTo, self)
                    mMod.triggered.connect(lambda: self.moveMod(item.row(), item.column(), 0))
                    self.rcmenu.addAction(mMod)
                    # -------------------move mod------------------
                    mMod = QAction(l.r.moveTop, self)
                    mMod.triggered.connect(lambda: self.moveMod(item.row(), item.column(), 1))
                    self.rcmenu.addAction(mMod)
                    # -------------------move mod------------------
                    mMod = QAction(l.r.moveBottom, self)
                    mMod.triggered.connect(lambda: self.moveMod(item.row(), item.column(), 2))
                    self.rcmenu.addAction(mMod)
                    # -------------------one mod-------------------
                    enableMod = QAction(l.r.switchState, self)
                    enableMod.triggered.connect(lambda: self.modSwitch(item.row(), item.column()))
                    self.rcmenu.addAction(enableMod)
                    # -------------------all mods-enable-----------
                    enableAllMod = QAction(l.r.enableAll, self)
                    enableAllMod.triggered.connect(lambda: self.modSwitchAll(1))
                    self.rcmenu.addAction(enableAllMod)
                    # -------------------all mods-disable----------
                    disableAllMod = QAction(l.r.disableAll, self)
                    disableAllMod.triggered.connect(lambda: self.modSwitchAll(0))
                    self.rcmenu.addAction(disableAllMod)
            return super(ModManager, self).eventFilter(source, event)
        except:
            self.logs.error("Unexpected error", exc_info=True)

    @pyqtSlot(str)
    def on_textChanged(self, text):
        try:
            for item in range(len(self.modList)):
                if text in self.modList[item].name and text != '':
                    self.filterList.append(self.modList[item].modID)
                    for i in range(4):
                        self.table.item(item, i).setBackground(QColor('yellow'))
                else:
                    if self.modList[item].modID in self.filterList:
                        if self.modList[item].isEnabled == 1:
                            for i in range(4):
                                self.table.item(item, i).setBackground(QColor.fromRgb(191, 245, 189))
                            self.filterList.remove(self.modList[item].modID)
                        else:
                            for i in range(4):
                                self.table.item(item, i).setBackground(QColor('white'))
                            self.filterList.remove(self.modList[item].modID)
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def generateMenu(self, pos):
        self.rcmenu.exec_(self.table.mapToGlobal(pos))

    def displayModData(self, row, column):
        try:
            self.retrieveData()
            self.modname.setText(self.modList[row].name)
            texttags = l.r.tagsForField
            texttags += self.modList[row].tags
            self.linkButton.disconnect()
            self.linkSteamButton.disconnect()
            self.linkButton.clicked.connect(lambda: webbrowser.open(self.url + str(self.modList[row].modID)))
            self.linkSteamButton.clicked.connect(lambda: webbrowser.open(self.steam_url + str(self.modList[row].modID)))
            if self.modList[row].source == 'local':
                self.linkButton.setVisible(0)
                self.linkSteamButton.setVisible(0)
                if self.modList[row].picture != '':
                    self.printModPreview(self.doc_folder + self.modList[row].path + '\\' + self.modList[row].picture)
                else:
                    self.printModPreview('nologo.png')
            else:
                self.linkButton.setVisible(1)
                self.linkSteamButton.setVisible(1)
                if self.modList[row].picture != '':
                    self.printModPreview(self.steam + self.modList[row].modID + '\\' + self.modList[row].picture)
                else:
                    self.printModPreview('nologo.png')
            self.textBrowser.setText(texttags)
            self.textBrowser.setMinimumSize(QSize(280, 35 + texttags.count('\n') * 25))
        except:
            self.logs.error("Unexpected error", exc_info=True)

# ------------------------технические методы--------------------------------
    def reloadOrder(self):
        try:
            self.modList = self.modListBackup
            self.idList = [mod.name for mod in self.modList]
            self.dataDisplay(self.modList)
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def retrieveData(self):
        modListNew = []
        for i in range(len(self.modList)):
            item = self.table.item(i, 1)
            ID = item.text()
            r = self.idList.index(ID)
            self.modList[r].prior = i
            modListNew.append(self.modList[r])
        self.modList = modListNew
        self.idList = [mod.name for mod in self.modList]

    def sortByType(self, btype):
        self.modList.sort(key=sortedKey, reverse=btype)
        self.dataDisplay(self.modList)

    def dumpLoadOrder(self):
        try:
            self.retrieveData()
            self.saveInDB()
            self.saveInGame()
            self.writeLoadOrder()
        except:
            print('error')
            self.logs.error("Unexpected error", exc_info=True)

    def getHelp(self):
        QMessageBox.about(self, l.r.helpLabel, l.r.helpContent)

# ------------------------запись в базу-------------------------------------
    def saveInDB(self):
        allFile = list()
        self.cursor.execute('DELETE FROM mods')
        self.conn.commit()
        for mod in self.modList:
            md = list()
            try:
                md.append(mod.name)
                md.append(mod.path)
                md.append(mod.modID)
                md.append(mod.version)
                md.append(mod.tags)
                md.append(mod.isEnabled)
                md.append(mod.source)
                md.append(mod.prior)
                md.append(mod.picture)
                md.append(mod.modfile)
            except KeyError:
                pass
            allFile.append(md)
        self.cursor.executemany("INSERT INTO mods VALUES (?,?,?,?,?,?,?,?,?,?)", allFile)
        self.conn.commit()

    def saveInGame(self):
        settingsFile = self.doc_folder + 'settings.txt'
        with open(settingsFile, 'r') as file:
            settingsList = file.readlines()
        text = ''
        for i in range(len(settingsList)):
            text += settingsList[i]
        active = re.search(r'last_mods={.*autosave', text, flags=re.DOTALL)
        newActive = 'last_mods={\n\t'
        for mod in self.modList:
            if mod.isEnabled == 1:
                if mod.source == 'steam':
                    newActive += '"mod/ugc_' + mod.modID + '.mod"\n\t'
                else:
                    newActive += '"mod/' + mod.modID + '.mod"\n\t'
        newActive = newActive[:-1]
        newActive += '}\nautosave'
        try:
            active = active.group(0)
        except AttributeError:
            active = re.search(r'autosave', text, flags=re.DOTALL)
            try:
                active = active.group(0)
            except AttributeError:
                pass
        text = text.replace(active, newActive)
        with open(settingsFile, 'w+', encoding='utf-8') as file:
            file.write(text)
            
    def writeLoadOrder(self):
        data = {}
        loadFile = self.doc_folder + 'dlc_load.json'
        with open(loadFile, 'r+') as json_file:
            data = json.load(json_file)
        summary = []
        for mod in self.modList:
            if mod.isEnabled == 1:
                if mod.source == 'steam':
                    modStr = 'mod/ugc_' + mod.modID + '.mod'
                else:
                    modStr = 'mod/' + mod.modID + '.mod'
                summary.append(modStr)
        data['enabled_mods'] = summary
        with open(loadFile, 'w') as json_file:
            json.dump(data, json_file)
