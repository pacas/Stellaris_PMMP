#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QWidget, QSizePolicy, QLabel
from PyQt5.QtWidgets import QGridLayout, QPushButton, QMessageBox
from PyQt5.QtCore import QSize, QPoint, Qt
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush, QFont
import threading
import os
import langSelector as l


class Launcher(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ----------------------------------
        self.setFixedSize(QSize(800, 600))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle('Launcher')
        self.setWindowIcon(QIcon('logo.png'))
        background = QImage('background.jpg')
        self.centralwidget = QWidget(self)
        self.centralwidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.gridLayout = QGridLayout(self.centralwidget)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)
        # ----------------------------------
        self.title = QLabel(' Stellaris PMMP', self.centralwidget)
        self.launch = QPushButton(l.r.launch, self.centralwidget)
        self.modmanager = QPushButton(l.r.modManager, self.centralwidget)
        self.options = QPushButton(l.r.options, self.centralwidget)
        self.exit = QPushButton(l.r.exitLabel, self.centralwidget)
        # ---layout-------------------------
        newfont = QFont('Times', 18, QFont.Bold)
        self.title.setStyleSheet('color: #3a86de;')
        self.title.setFont(newfont)
        self.title.setFixedSize(QSize(400, 40))
        self.gridLayout.addWidget(self.title, 0, 0)
        self.launch.setFixedSize(QSize(200, 70))
        self.gridLayout.addWidget(self.launch, 1, 0)
        self.modmanager.setFixedSize(QSize(200, 70))
        self.gridLayout.addWidget(self.modmanager, 2, 0)
        self.options.setFixedSize(QSize(200, 70))
        self.gridLayout.addWidget(self.options, 3, 0)
        self.exit.setFixedSize(QSize(200, 70))
        self.gridLayout.addWidget(self.exit, 4, 0)
        # ---launcher-version---------------
        self.version = QLabel('v1.0', self.centralwidget)
        p = self.geometry().bottomLeft() - self.version.geometry().bottomLeft() - QPoint(-10, 10)
        self.version.move(p)
        self.version.setStyleSheet('font-size: 14pt; color: #3a86de;')
        # ----------------------------------
        self.setCentralWidget(self.centralwidget)

    def gamestart(self, game):
        try:
            d = threading.Thread(name='daemon', target=os.startfile(game))
            d.setDaemon(True)
            d.start()
        except OSError as err:
            QMessageBox.about(self, l.r.warning, l.r.warningDesc1)
            print("OS error: {0}".format(err))
