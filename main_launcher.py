#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QWidget, QSizePolicy, QLabel
from PyQt5.QtWidgets import QGridLayout, QPushButton, QMessageBox
from PyQt5.QtCore import QSize, QPoint, Qt
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush
import threading
import os
import langSelector as l
import design.styles as style
import files_const as pth


class Launcher(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ----------------------------------
        self.setFixedSize(QSize(800, 600))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle('Launcher')
        self.setWindowIcon(QIcon(pth.logo))
        background = QImage(pth.background_launcher)
        self.centralwidget = QWidget(self)
        self.centralwidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.gridLayout = QGridLayout(self.centralwidget)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)
        # ----------------------------------
        self.title = QLabel('  ', self.centralwidget)  # заглушка
        self.launch = QPushButton(l.r.launch, self.centralwidget)
        self.modmanager = QPushButton(l.r.modManager, self.centralwidget)
        self.options = QPushButton(l.r.options, self.centralwidget)
        self.exit = QPushButton(l.r.exitLabel, self.centralwidget)
        # ---layout-------------------------
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
        self.version = QLabel('v1.0.3.1', self.centralwidget)
        p = self.geometry().bottomLeft() - self.version.geometry().bottomLeft() - QPoint(-10, 10)
        self.version.move(p)
        self.version.setStyleSheet(style.launcher_version)
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
