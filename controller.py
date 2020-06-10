#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox, QWidget
import main_launcher as launcher
import submenu_options as options
import submenu_backups as backups
import main_mod_manager as manager
import sys
import os
import psutil
import logging


class Controller(QWidget):
    def __init__(self):
        super().__init__()
        self.gamepath = ''
        if not os.path.exists("logs"):
            os.mkdir("logs")
        self.logs = logging.getLogger("St-PLP")
        handler = logging.FileHandler(filename = "logs/err-launcher.log", mode="w")
        self.logs.setLevel(logging.ERROR)
        self.logs.addHandler(handler)
        try:
            self.first_Launch()
            self.show_Launcher()
            self.Launcher.modmanager.clicked.connect(self.show_ModManager)
            self.Launcher.options.clicked.connect(self.show_Options)
            self.Launcher.exit.clicked.connect(self.close_Launcher)
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def show_Launcher(self):
        try:
            self.Launcher = launcher.Launcher()
            self.Launcher.launch.clicked.connect(lambda: self.Launcher.gamestart(self.gamepath + '/stellaris.exe'))
            self.Launcher.show()
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def show_ModManager(self):
        try:
            self.ModManager = manager.ModManager()
            self.ModManager.openBackupMenu.triggered.connect(self.show_Backups)
            self.ModManager.exitACT.triggered.connect(lambda: self.ModManager.close())
            self.ModManager.set_Game_Location(self.gamepath)
            self.ModManager.show()
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def show_Options(self):
        try:
            self.Options = options.Options()
            self.Options.closew.clicked.connect(lambda: self.Options.close())
            self.Options.show()
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def show_Backups(self):
        try:
            self.Backups = backups.Backups()
            self.Backups.make.clicked.connect(lambda: self.Backups.make_Backup(self.ModManager.modList))
            self.Backups.load.clicked.connect(lambda: self.load_From_Backup_Connect())
            self.Backups.delete.clicked.connect(lambda: self.remove_Backup())
            self.Backups.closew.clicked.connect(lambda: self.Backups.close())
            self.Backups.show()
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def load_From_Backup_Connect(self):
        try:
            index = self.Backups.table.selectionModel().selectedRows()
            cell = self.Backups.table.item(index[0].row(), 0).text()
            newModList = self.Backups.load_From_Backup(self.ModManager.modList, cell)
            self.ModManager.dataDisplay(newModList)
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def remove_Backup(self):
        try:
            index = self.Backups.table.selectionModel().selectedRows()
            cell = self.Backups.table.item(index[0].row(), 0).text()
            os.remove('backup/' + cell + '.bak')
            self.Backups.dataDisplay()
        except:
            self.logs.error("Unexpected error", exc_info=True)

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
        self.get_Disk_Links()
        try:
            with open('launcher-settings.ini', 'r', encoding='UTF-8') as settings:
                data = settings.readline()
                self.gamepath = data[14:]
        except FileNotFoundError:
            if self.check == 0:
                QMessageBox.about(self, "Attention", "Please enter your game location in the next window (C:/Steam/steamapps/common/Stellaris as example)")
                self.gamepath, okPressed = QInputDialog.getText(self, 'Attention', 'Game location:', QLineEdit.Normal, '')
                if okPressed and self.gamepath != '':
                    self.ini_Write(self.gamepath)
                    QMessageBox.about(self, 'Warning', 'Attention, if this is your first launch of the mod manager, it is strongly recommended delete files dlc_load, game_data and mods_registry in your Documents/Paradox Interactive/Stellaris folder with making a backup of them and start default launcher once. After this YOU MUST ENABLE ALL MODS IN MODLIST! Do not ask me why. It`s just works. This will delete the boot order and the list of enabled mods, but can help to avoid many errors.')
                else:
                    QMessageBox.about(self, 'Warning', 'Enter valid name')
                    # зациклить на ожидание правильного ввода
                    self.close_Launcher()
            else:
                self.gamepath = self.steam
                self.ini_Write(self.steam)

    def get_Disk_Links(self):
        try:
            self.steam = '/Steam/steamapps/common/Stellaris/'
            disks = psutil.disk_partitions()
            self.check = 0
            for disk in disks:
                if os.path.exists(disk.device + self.steam) is True:
                    self.steam = disk.device + self.steam
                    self.check = 1
                    break
        except:
            self.logs.error("Unexpected error", exc_info=True)

    def ini_Write(self, path):
        try:
            with open('launcher-settings.ini', 'w+', encoding='UTF-8') as settings:
                settings.write('game_location=' + path)
        except FileNotFoundError:
            QMessageBox.about(self, "Warning", "Error")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet('QPushButton {border: 3px solid #8f8f91; border-radius: 13px; background-color: #f6f7fa;} QPushButton:pressed {background-color: #adadad;}')
    Controller = Controller()
    sys.exit(app.exec())
