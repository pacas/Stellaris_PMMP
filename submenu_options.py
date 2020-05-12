#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QWidget, QSizePolicy, QLabel
from PyQt5.QtWidgets import QGridLayout, QComboBox
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush

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
        self.windowtype.currentIndexChanged.connect(self.windowchange)
        # ----------------------------------
        self.wsizename = QLabel('Screen resolution', self.centralwidget)
        self.wsize = QComboBox(self.centralwidget)
        self.wsize.addItems(['1920x1080', '3840x2160', '1680x1050', '1600x1024', '1600x900', '1440x900', '1366x768', '1360x768', '1280x1024', '1280x960', '1280x800', '1280x768', '1280x720', '1176x664', '1152x864', '1024x768'])
        # ----------------------------------
        self.langname = QLabel('Language', self.centralwidget)
        self.lang = QComboBox(self.centralwidget)
        self.lang.addItems(['English', 'Russian', 'Deutsch', 'Polski', 'Portuguese', 'French', 'Spanish', 'Chinese'])
        # ---layout-------------------------
        self.gridLayout.addWidget(self.windowname, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.windowtype, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.wsizename, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.wsize, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.langname, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.lang, 2, 2, 1, 1)
        # ----------------------------------
        self.setCentralWidget(self.centralwidget)
    
    def windowchange(self, i):
        pass
