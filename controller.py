#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QApplication
import main_launcher as launcher
import submenu_options as options
import submenu_backups as backups
import current_version5 as manager
import sys
import os


class Controller:
    def __init__(self):
        self.show_Launcher()
        self.Launcher.modmanager.clicked.connect(self.show_ModManager)
        self.Launcher.options.clicked.connect(self.show_Options)
        self.Launcher.exit.clicked.connect(self.close_Launcher)

    def show_Launcher(self):
        self.Launcher = launcher.Launcher()
        self.Launcher.show()

    def show_ModManager(self):
        self.ModManager = manager.ModManager()
        self.ModManager.openBackupMenu.triggered.connect(self.show_Backups)
        self.ModManager.show()

    def show_Options(self):
        self.Options = options.Options()
        self.Options.show()
    
    def show_Backups(self):
        self.Backups = backups.Backups()
        self.Backups.make.clicked.connect(lambda: self.Backups.makeBackup(self.ModManager.modList))
        self.Backups.load.clicked.connect(lambda: self.loadFromBackupConnect())
        self.Backups.delete.clicked.connect(lambda: self.removeVackup())
        self.Backups.closew.clicked.connect(lambda: self.Backups.close())
        self.Backups.show()
        
    def loadFromBackupConnect(self):
        index = self.Backups.table.selectionModel().selectedRows()
        cell = self.Backups.table.item(index[0].row(), 0).text()
        newModList = self.Backups.loadFromBackup(self.ModManager.modList, cell)
        self.ModManager.dataDisplay(newModList)
        
    def removeVackup(self):
        index = self.Backups.table.selectionModel().selectedRows()
        cell = self.Backups.table.item(index[0].row(), 0).text()
        os.remove('backup/' + cell + '.bak')
        self.Backups.dataDisplay()
    
    # добавить везде кнопки закрытия и убрать эту функцию
    def close_Launcher(self):
        try:
            self.ModManager.close()
        except AttributeError:
            pass
        try:
            self.Options.close()
        except AttributeError:
            pass
        try:
            self.Launcher.close()
        except AttributeError:
            pass
        try:
            self.Backups.close()
        except AttributeError:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet('QPushButton {border: 3px solid #8f8f91; border-radius: 13px; background-color: #f6f7fa;} QPushButton:pressed {background-color: #adadad;}')
    Controller = Controller()
    sys.exit(app.exec())
