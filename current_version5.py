#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QAction, QMainWindow, QWidget, QSizePolicy, QLabel
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QPushButton, QHeaderView, QSpacerItem, QTextBrowser
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QPixmap, QFont, QIcon
import json
import glob
from os import listdir
import webbrowser
import feature_dnd as dnd

def TestDiffBug():
    mod_ugc = 'C:/Users/User/Documents/Paradox Interactive/Stellaris/mod/ugc_*.mod'
    mod_folders = 'M:/Steam/steamapps/workshop/content/281990/'
    descriptors = set()
    globlist = glob.glob(mod_ugc)
    for i in globlist:
        i = i[len(mod_ugc) - 5:-4]
        descriptors.add(i)
    folders = listdir(mod_folders)
    folders = set(folders)
    differ = descriptors.symmetric_difference(folders)
    return len(differ) == 0

def sortedKey(mod):
    return mod.sortedKey


class Mod():
    def __init__(self, hashID, name, modID, version, tags, source, steamID, dirPath, archivePath, isEnabled):
        self.hashID = hashID
        self.name = name
        self.modID = modID
        self.version = version
        self.tags = tags
        self.source = source
        self.steamID = steamID
        self.dirPath = dirPath
        self.archivePath = archivePath
        self.isEnabled = isEnabled
        self.sortedKey = name.encode('utf8', errors='ignore')

# мод менеджер
class ModManager(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ---definitions--------------------
        self.dlc_load = 'dlc_load.json'
        self.mods_registry = 'mods_registry.json'
        self.mods_data = 'mods_data.json'
        self.game_data = 'game_data.json'
        # self.folder = 'backup'
        self.url = 'https://steamcommunity.com/sharedfiles/filedetails/?id='
        self.modsloc = 'M:/Steam/steamapps/workshop/content/281990/'
        # ----------------------------------
        self.setMinimumSize(QSize(1200, 700))
        self.setWindowTitle('Mod Manager')
        self.setWindowIcon(QIcon('logo.png'))
        # ---central widget----------------
        self.centralwidget = QWidget(self)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.centralwidget.setMinimumSize(QSize(1200, 700))
        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # ---table widget-------------------
        self.table = dnd.TableWidgetDragRows()
        self.table.setColumnCount(4)
        self.header = self.table.horizontalHeader()
        self.header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setMinimumSize(QSize(800, 300))
        self.horizontalLayout.addWidget(self.table, 0)
        self.verticalLayout = QVBoxLayout()
        # ---modname------------------------
        self.modname = QLabel('Информация о модификации', self.centralwidget)
        self.modname.setMinimumSize(QSize(320, 100))
        newfont = QFont('Times', 18, QFont.Bold)
        self.modname.setFont(newfont)
        self.modname.setWordWrap(True)
        self.modname.setAlignment(Qt.AlignHCenter)
        self.verticalLayout.addWidget(self.modname, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        # ---preview pic--------------------
        self.pic = QLabel()
        self.printModPreview(None)
        self.verticalLayout.addWidget(self.pic, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.verticalLayout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
        # ---mod description----------------
        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setMaximumSize(QSize(550, 40000))
        newfont = QFont('Verdana', 13, QFont.Bold)
        self.textBrowser.setFont(newfont)
        self.verticalLayout.addWidget(self.textBrowser, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        # ---link button--------------------
        self.verticalLayout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.linkButton = QPushButton('Открыть страницу в мастерской', self.centralwidget)
        self.linkButton.setMinimumSize(QSize(300, 30))
        self.linkButton.setMaximumSize(QSize(300, 30))
        self.verticalLayout.addWidget(self.linkButton, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        # ---finalizing---------------------
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.setCentralWidget(self.centralwidget)
        # ----------------------------------
        self.modList = []
        self.getModData(self.mods_registry, self.dlc_load, self.game_data)
        # ----------------------------------
        self.menu = self.menuBar()
        # ---program------------------------
        prMenu = self.menu.addMenu('&Program')
        dumpACT = QAction('Save load order', self)
        # dumpACT.setShortcut('Ctrl+S')
        dumpACT.triggered.connect(self.dumpLoadOrder)
        prMenu.addAction(dumpACT)
        # ---sorting------------------------
        orderMenu = self.menu.addMenu('&Sorting')
        orderACT = QAction('Sort in alphabetical order', self)
        orderACT.triggered.connect(lambda: self.sortByType(True))
        orderMenu.addAction(orderACT)
        # ----------------------------------
        orderACT = QAction('Sort in reverse alphabetical order', self)
        orderACT.triggered.connect(lambda: self.sortByType(False))
        orderMenu.addAction(orderACT)
        # ---backups------------------------
        backupMenu = self.menu.addMenu('&Backups')
        # ----------------------------------
        self.openBackupMenu = QAction('Open backup menu', self)
        backupMenu.addAction(self.openBackupMenu)
        # ----------------------------------
        self.dataDisplay(self.modList)
        self.table.cellDoubleClicked.connect(self.onCellChanged)
        self.table.cellClicked.connect(self.displayModData)

    # получение описания мода из мастерской
    '''
    def getSteamDesc(self, mid):
        response = requests.get(self.url + mid)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.find(class_='workshopItemDescription')
        final = str(text)
        final = final[59:-6]
        self.textBrowser.setHtml(final)
    '''

    def printModPreview(self, image):
        self.tmp = QPixmap(image)
        self.tmp = self.tmp.scaled(256, 256, Qt.KeepAspectRatio)
        self.pic.setPixmap(self.tmp)

    # получение данных из файлов
    def getModData(self, m, d, g):
        with open(m, encoding='UTF-8') as gameData:
            data = json.load(gameData)
            self.getModList(data)
            self.createModList()
        # ----------------------------------
        with open(d, encoding='UTF-8') as loadOrder:
            data = json.load(loadOrder)
            self.getLoadList(data)
        # ----------------------------------
        # добавить проверку на первый запуск через  файл настроек
        with open(g, encoding='UTF-8') as dataOrder:
            data = json.load(dataOrder)
            self.getDisplayList(data)
        self.idList = [mod.modID for mod in self.modList]

    def getModList(self, data):
        for hashID, data in data.items():
            try:
                name = data['displayName']
                modID = data['gameRegistryId']
                source = data['source']
                try:
                    version = data['requiredVersion']
                except KeyError:
                    version = '---'
                    with open(modID) as file:
                        for text in file:
                            if 'version="' in text:
                                text.strip()
                                version = text[9:-2]
                                break
                try:
                    steamID = data['steamId']
                except KeyError:
                    steamID = ''
                try:
                    tags = data['tags']
                except KeyError:
                    tags = ''
                dirPath = data['dirPath']
                try:
                    archivePath = data['archivePath']
                except KeyError:
                    archivePath = ''
                mod = Mod(hashID, name, modID, version, tags, source, steamID, dirPath, archivePath, isEnabled=0)
                self.modList.append(mod)
            except KeyError:
                print('key not found in ', name)

    # получение текущего списка загрузки (включённые моды)
    def getLoadList(self, data):
        load = data['enabled_mods']
        for i in load:
            for j in self.modList:
                if str(i) == j.modID:
                    j.isEnabled = 1
                    break

    # получение текущего списка загрузки (порядок)
    def getDisplayList(self, data):
        load = data['modsOrder']
        newOrder = []
        for i in load:
            for j in self.modList:
                if str(i) == j.hashID:
                    newOrder.append(j)
                    continue
        self.modList = newOrder

    # удаление лишних модов в списке
    def removeBadModInfo(self):
        for mod in self.modList:
            if mod.modID not in self.realModList:
                # print('|', mod.name, '|', mod.modID, '|')
                self.modList.remove(mod)
            else:
                self.realModList.remove(mod.modID)
        if self.realModList != []:
            self.newModsInfo()

    # обновление таблицы
    def dataDisplay(self, modList):
        self.table.setRowCount(0)
        self.table.setRowCount(len(modList))
        labels = ['Path', 'Name', 'Version', 'Source']
        self.table.setHorizontalHeaderLabels(labels)
        for i in range(3):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)

        counter = 0
        for mod in modList:
            # ----------------------------------
            self.table.setItem(counter, 0, QTableWidgetItem(mod.modID))
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
            if mod.isEnabled == 1:
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
            self.modList[row].isEnabled = 1
        else:
            for i in range(4):
                self.table.item(row, i).setBackground(QColor('white'))
            self.modList[row].isEnabled = 0

    def displayModData(self, row, column):
        self.modname.setText(self.modList[row].name)
        preview = ''
        texttags = 'Tags:\n'
        self.linkButton.disconnect()
        self.linkButton.clicked.connect(lambda: webbrowser.open(self.url + str(self.modList[row].steamID)))
        with open(self.modList[row].modID) as file:
            for text in file:
                if 'picture="' in text:
                    text.strip()
                    preview = text[9:-2]
                    break
        if self.modList[row].source == 'local':
            self.printModPreview('mod/' + preview)
            self.linkButton.setVisible(0)
        else:
            self.printModPreview(self.modsloc + self.modList[row].steamID + '/' + preview)
            self.linkButton.setVisible(1)
        for tag in self.modList[row].tags:
            texttags += tag
            texttags += '\n'
        self.textBrowser.setText(texttags)

    def retrieveData(self):
        modListNew = []
        for i in range(len(self.modList)):
            item = self.table.item(i, 0)
            ID = item.text()
            r = self.idList.index(ID)
            modListNew.append(self.modList[r])
        self.modList = modListNew
        self.idList = [mod.modID for mod in self.modList]

    # методы для меню
    def sortByType(self, btype):
        self.modList.sort(key=sortedKey, reverse=btype)
        self.dataDisplay(self.modList)

    def dumpLoadOrder(self):
        self.retrieveData()
        self.writeLoadOrder()
        self.writeDisplayOrder()

    # запись в файлы
    def createModList(self):
        allFile = dict()
        for mod in self.modList:
            md = dict()
            try:
                md.update([('displayName', mod.name)])
                md.update([('gameRegistryId', mod.modID)])
                md.update([('source', mod.source)])
                if mod.steamID != '':
                    md.update([('steamId', mod.steamID)])
                md.update([('requiredVersion', mod.version)])
                md.update([('dirPath', mod.dirPath)])
                if mod.archivePath != '':
                    md.update([('archivePath', mod.archivePath)])
                md.update([('status', 'ready_to_play')])
                md.update([('id', mod.hashID)])
            except KeyError:
                print('error in ', mod.name)
            allFile.update([(mod.hashID, md)])
        with open(self.mods_data, 'w', encoding='utf-8') as json_file:
            json.dump(allFile, json_file, ensure_ascii=False)
        with open(self.mods_data, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        lines = [line.replace('": ', '":') for line in lines]
        lines = [line.replace('", "', '","') for line in lines]
        lines = [line.replace('"}, ', '"},') for line in lines]
        with open(self.mods_data, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        # os.remove(self.mods_registry)
        # copyfile(self.mods_data, self.mods_registry)

    # запись включённых модов
    def writeLoadOrder(self):
        data = {}
        with open(self.dlc_load, 'r+') as json_file:
            data = json.load(json_file)
        summary = []
        for mod in self.modList:
            if mod.isEnabled == 1:
                summary.append(mod.modID)
        data['enabled_mods'] = summary
        with open('dlc_load1.json', 'w') as json_file:
            json.dump(data, json_file)

    # запись порядка загрузки
    def writeDisplayOrder(self):
        data = {}
        with open(self.game_data, 'r+') as json_file:
            data = json.load(json_file)
        summary = []
        for mod in self.modList:
            summary.append(mod.hashID)
        data['modsOrder'] = summary
        with open('game_data1.json', 'w') as json_file:
            json.dump(data, json_file)

    # запись зарегистрированных модов
    # сделать
    def writeModsInfo(self):
        data = {}
        with open(self.mods_registry, 'r+') as json_file:
            data = json.load(json_file)
        summary = []
        for mod in self.modList:
            summary.append(mod.hashID)
        data['modsOrder'] = summary
        with open('game_data.json', 'w') as json_file:
            json.dump(data, json_file)