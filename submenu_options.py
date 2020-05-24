#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QWidget, QSizePolicy, QLabel
from PyQt5.QtWidgets import QGridLayout, QComboBox, QPushButton
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush
import os


class Options(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ----------------------------------
        self.setFixedSize(QSize(800, 600))
        self.setWindowTitle('Options')
        self.setWindowIcon(QIcon('logo.png'))
        background = QImage('background.jpg')
        self.centralwidget = QWidget(self)
        self.centralwidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.gridLayout = QGridLayout(self.centralwidget)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)
        self.setStyleSheet('QLabel {font-size: 12pt; color: #3a86de;}')
        # ----------------------------------
        self.windowname = QLabel('Display mode', self.centralwidget)
        self.windowtype = QComboBox(self.centralwidget)
        self.windowtype.addItems(['Fullscreen', 'Borderless', 'Window'])
        self.windowtype.currentIndexChanged.connect(self.displayChange)
        # ----------------------------------
        self.wsizename = QLabel('Screen resolution', self.centralwidget)
        self.wsize = QComboBox(self.centralwidget)
        self.wsize.addItems(['1920x1080', '3840x2160', '1680x1050', '1600x1024', '1600x900', '1440x900', '1366x768', '1360x768', '1280x1024', '1280x960', '1280x800', '1280x768', '1280x720', '1176x664', '1152x864', '1024x768'])
        self.wsize.currentIndexChanged.connect(self.resChange)
        # ----------------------------------
        self.langname = QLabel('Language', self.centralwidget)
        self.lang = QComboBox(self.centralwidget)
        self.lang.addItems(['English', 'Russian', 'Deutsch', 'Polski', 'Portuguese', 'French', 'Spanish', 'Chinese'])
        self.lang.currentIndexChanged.connect(self.langChange)
        # ----------------------------------
        self.saves = QPushButton('Save settings', self.centralwidget)
        self.saves.clicked.connect(self.saveSettings)
        self.saves.setFixedSize(QSize(230, 60))
        self.closew = QPushButton('Close', self.centralwidget)
        self.closew.setFixedSize(QSize(230, 60))
        # self.empty = QLabel('', self.centralwidget)
        # self.empty.setFixedSize(QSize(30, 10))
        # ---layout-------------------------
        self.gridLayout.addWidget(self.windowname, 0, 0, 1, 1)
        # self.gridLayout.addWidget(self.empty, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.windowtype, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.wsizename, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.wsize, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.langname, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.lang, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.saves, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.closew, 3, 2, 1, 1)
        # ----------------------------------
        self.settingsRead()
        self.setCentralWidget(self.centralwidget)

    def settingsRead(self):
        self.settings = os.path.join(os.path.expanduser('~'), 'Documents', 'Paradox Interactive', 'Stellaris', 'settings.txt')
        with open(self.settings, 'r') as file:
            self.stList = file.readlines()
        # ----------------------------------
        if self.stList[16] == '\tfullScreen=yes\n' and self.stList[17] == '\tborderless=no\n':
            index = self.windowtype.findText('Fullscreen', Qt.MatchFixedString)
        elif self.stList[16] == '\tfullScreen=no\n' and self.stList[17] == '\tborderless=yes\n':
            index = self.windowtype.findText('Borderless', Qt.MatchFixedString)
        else:
            index = self.windowtype.findText('Window', Qt.MatchFixedString)
        self.windowtype.setCurrentIndex(index)
        # ----------------------------------
        text = self.stList[4][4:-1] + 'x' + self.stList[5][4:-1]
        index1 = self.wsize.findText(text, Qt.MatchFixedString)
        self.wsize.setCurrentIndex(index1)
        # ----------------------------------
        text = self.stList[1][12:-2].capitalize()
        if text == 'Simp_chinese':
            index2 = self.lang.findText('Chinese', Qt.MatchFixedString)
        elif text == 'German':
            index2 = self.lang.findText('Deutsch', Qt.MatchFixedString)
        elif text == 'Braz_por':
            index2 = self.lang.findText('Portuguese', Qt.MatchFixedString)
        elif text == 'Polish':
            index2 = self.lang.findText('Polski', Qt.MatchFixedString)
        else:
            index2 = self.lang.findText(text, Qt.MatchFixedString)
        self.lang.setCurrentIndex(index2)
        # ----------------------------------

        '''
        язык       i = 1
        8 вариантов
        разрешение i = 4,5,9,10
        16 вариантов
        fullscreen i = 16
        borderless i = 17
        '''

    def displayChange(self, d):
        if d == 0:
            self.stList[16] = '\tfullScreen=yes\n'
            self.stList[17] = '\tborderless=no\n'
        elif d == 1:
            self.stList[16] = '\tfullScreen=no\n'
            self.stList[17] = '\tborderless=yes\n'
        else:
            self.stList[16] = '\tfullScreen=no\n'
            self.stList[17] = '\tborderless=no\n'

    def langAdd(self, i, j):
        self.stList[4] = '\t\tx=' + str(i) + '\n'
        self.stList[5] = '\t\ty=' + str(j) + '\n'
        self.stList[9] = '\t\tx=' + str(i) + '\n'
        self.stList[10] = '\t\ty=' + str(j) + '\n'

    def resChange(self, lang):
        if lang == 0:
            self.langAdd(1920, 1080)
        elif lang == 1:
            self.langAdd(3840, 2160)
        elif lang == 2:
            self.langAdd(1680, 1050)
        elif lang == 3:
            self.langAdd(1600, 1024)
        elif lang == 4:
            self.langAdd(1600, 900)
        elif lang == 5:
            self.langAdd(1440, 900)
        elif lang == 6:
            self.langAdd(1366, 768)
        elif lang == 7:
            self.langAdd(1360, 768)
        elif lang == 8:
            self.langAdd(1280, 1024)
        elif lang == 9:
            self.langAdd(1280, 960)
        elif lang == 10:
            self.langAdd(1280, 800)
        elif lang == 11:
            self.langAdd(1280, 768)
        elif lang == 12:
            self.langAdd(1280, 720)
        elif lang == 13:
            self.langAdd(1176, 664)
        elif lang == 14:
            self.langAdd(1152, 864)
        else:
            self.langAdd(1024, 768)

    def langChange(self, i):
        if i == 0:
            self.stList[1] = 'language="l_english"\n'
        elif i == 1:
            self.stList[1] = 'language="l_russian"\n'
        elif i == 2:
            self.stList[1] = 'language="l_german"\n'
        elif i == 3:
            self.stList[1] = 'language="l_polish"\n'
        elif i == 4:
            self.stList[1] = 'language="l_braz_por"\n'
        elif i == 5:
            self.stList[1] = 'language="l_french"\n'
        elif i == 6:
            self.stList[1] = 'language="l_spanish"\n'
        else:
            self.stList[1] = 'language="l_simp_chinese"\n'

    def saveSettings(self):
        with open(self.settings, 'w+', encoding='utf-8') as file:
            for line in self.stList:
                file.write(line)
