#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox, QWidget
import main_launcher as launcher
import submenu_options as options
import submenu_backups as backups
import main_mod_manager as manager
import sys
import os


class Controller(QWidget):
    def __init__(self):
        super().__init__()
        self.gamepath = ''
        self.first_Launch()
        self.show_Launcher()
        self.Launcher.modmanager.clicked.connect(self.show_ModManager)
        self.Launcher.options.clicked.connect(self.show_Options)
        self.Launcher.exit.clicked.connect(self.close_Launcher)

    def show_Launcher(self):
        self.Launcher = launcher.Launcher()
        self.Launcher.launch.clicked.connect(lambda: self.Launcher.gamestart(self.gamepath + '\stellaris.exe'))
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
        self.Backups.make.clicked.connect(lambda: self.Backups.make_Backup(self.ModManager.modList))
        self.Backups.load.clicked.connect(lambda: self.load_From_Backup_Connect())
        self.Backups.delete.clicked.connect(lambda: self.remove_Backup())
        self.Backups.closew.clicked.connect(lambda: self.Backups.close())
        self.Backups.show()
        
    def load_From_Backup_Connect(self):
        index = self.Backups.table.selectionModel().selectedRows()
        cell = self.Backups.table.item(index[0].row(), 0).text()
        newModList = self.Backups.load_From_Backup(self.ModManager.modList, cell)
        self.ModManager.dataDisplay(newModList)
        
    def remove_Backup(self):
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
    
    def first_Launch(self):
        try:
            with open('laucher-settings.ini', 'r', encoding='UTF-8') as settings:
                data = settings.readline()
                self.gamepath = data[14:]
        except FileNotFoundError:
            QMessageBox.about(self, "Attention", "Please enter your game location in the next window (C:\Steam\steamapps\common\Stellaris as example)")
            self.gamepath, okPressed = QInputDialog.getText(self, 'Attention', 'Game location:', QLineEdit.Normal, '')
            if okPressed and self.gamepath != '':
                try:
                    with open(self.gamepath + '\laucher-settings.ini', 'w+', encoding='UTF-8') as settings:
                        settings.write('game_location=' + self.gamepath)
                except:
                    QMessageBox.about(self, "Warning", "Error")
            else:
                QMessageBox.about(self, "Warning", "Enter valid name")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet('QPushButton {border: 3px solid #8f8f91; border-radius: 13px; background-color: #f6f7fa;} QPushButton:pressed {background-color: #adadad;}')
    Controller = Controller()
    sys.exit(app.exec())
