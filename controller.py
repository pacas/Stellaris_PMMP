#!/usr/bin/python3
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox, QWidget
import main_launcher as launcher
import submenu_options as options
import submenu_backups as backups
import main_mod_manager as manager
import sys
import os
from psutil import disk_partitions
import logging
import sqlite3
import atexit
import design.styles as style
import files_const as pth


class Controller(QWidget):
    def __init__(self):
        super().__init__()
        self.gamepath = ''
        self.get_connection()
        # ----------Logging-----------------
        if not os.path.exists(pth.logs_folder):
            os.mkdir(pth.logs_folder)
        self.logs = logging.getLogger("St-PLP")
        handler = logging.FileHandler(filename=pth.logs_launcher, mode="a+")
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        handler.setFormatter(formatter)
        self.logs.setLevel(logging.ERROR)
        self.logs.addHandler(handler)
        # --------Launcher window-----------
        try:
            self.get_Disk_Links()
            self.first_Launch()
            self.show_Launcher()
            self.Launcher.modmanager.clicked.connect(self.show_ModManager)
            self.Launcher.options.clicked.connect(self.show_Options)
            self.Launcher.exit.clicked.connect(self.close_Launcher)
        except Exception as err:
            self.logs.error(err, exc_info=True)

# ------------------- Windows methods--------------------------
    def show_Launcher(self):
        try:
            self.Launcher = launcher.Launcher()
            self.Launcher.launch.clicked.connect(lambda: self.Launcher.gamestart(self.gamepath + '/stellaris.exe'))
            self.Launcher.show()
        except Exception as err:
            self.logs.error(err, exc_info=True)

    def show_ModManager(self):
        try:
            self.ModManager = manager.ModManager(self.launch, self.conn, self.cursor)
            self.ModManager.setStyleSheet(style.mm_buttons)
            self.ModManager.openBackupMenu.triggered.connect(self.show_Backups)
            self.ModManager.exitACT.triggered.connect(lambda: self.ModManager.close())
            self.ModManager.exitButton.clicked.connect(lambda: self.ModManager.close())
            self.ModManager.set_Game_Location(self.gamepath)
            self.ModManager.show()
            self.launch = 0
        except Exception as err:
            self.logs.error(err, exc_info=True)

    def show_Options(self):
        try:
            self.Options = options.Options()
            self.Options.closew.clicked.connect(lambda: self.Options.close())
            self.Options.show()
        except Exception as err:
            self.logs.error(err, exc_info=True)

    def show_Backups(self):
        try:
            self.Backups = backups.Backups()
            self.Backups.setStyleSheet(style.backups_buttons)
            self.Backups.make.clicked.connect(lambda: self.Backups.make_Backup(self.ModManager.modList))
            self.Backups.load.clicked.connect(lambda: self.load_From_Backup_Connect())
            self.Backups.delete.clicked.connect(lambda: self.Backups.remove_Backup())
            self.Backups.closew.clicked.connect(lambda: self.Backups.close())
            self.Backups.show()
        except Exception as err:
            self.logs.error(err, exc_info=True)

# -----------Connection between backup and MM modules----------
    def load_From_Backup_Connect(self):
        try:
            index = self.Backups.table.selectionModel().selectedRows()
            cell = self.Backups.table.item(index[0].row(), 0).text()
            newModList = self.Backups.load_From_Backup(self.ModManager.modList, cell)
            self.ModManager.dataDisplay(newModList)
            self.ModManager.modList = newModList
        except Exception as err:
            self.logs.error(err, exc_info=True)

# ------------------- DB connections --------------------------
    def get_connection(self):
        self.conn = sqlite3.connect(pth.DB)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS mods 
                            (name text, path text, modID text, version text, 
                             tags text, state bit, source text, prior int, 
                             picture text, modfile text)''')
        self.conn.commit()
        atexit.register(self.close_connection, self.conn)

    def close_connection(self, conn):
        print('Connection closed')
        conn.commit()
        conn.close()

# -------------------I WILL CLOSE THIS ALL----------------------
    def close_Launcher(self):
        self.close_connection(self.conn)
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

# -----------------Launcher settings and ini file--------------
# I want to believe that no one will break this function, because I'm too lazy to rewrite it
    def first_Launch(self):
        try:
            with open(pth.ini_file, 'r', encoding='UTF-8') as settings:
                data = settings.readlines()
                self.gamepath = data[0][14:-1]
                self.lang = data[1][5:]
                self.launch = 0
        except FileNotFoundError:
            self.launch = 1
            if self.check == 0:
                print("\a")
                QMessageBox.about(self, "Attention", 
                                  '''Please enter your game location in the next window 
                                  (C:/Steam/steamapps/common/Stellaris as example)''')
                self.gamepath, okPressed = QInputDialog.getText(self, 'Attention', 'Game location:', QLineEdit.Normal, '')
                if okPressed:
                    test = self.gamepath + '\\stellaris.exe'
                    if os.path.isfile(test):
                        self.ini_Write(self.gamepath, 'eng')
                        print("\a")
                        QMessageBox.about(self, 'Warning', 
                                          '''Attention, if this is your first launch of the mod manager, 
                                          YOU MUST RUN THE GAME AT LEAST ONCE!''')
                    else:
                        print("\a")
                        QMessageBox.about(self, 'Warning', 'Enter valid name')
                        self.first_Launch()
                else:
                    print("\a")
                    QMessageBox.about(self, 'Warning', 'Enter valid name')
                    self.first_Launch()
            else:
                self.gamepath = self.steam
                self.ini_Write(self.steam, 'eng')

    def get_Disk_Links(self):
        try:
            self.steam = '/Steam/steamapps/common/Stellaris/'
            disks = disk_partitions()
            self.check = 0
            for disk in disks:
                if os.path.exists(disk.device + self.steam) is True:
                    self.steam = disk.device + self.steam
                    self.check = 1
                    break
        except Exception as err:
            self.logs.error(err, exc_info=True)

    def ini_Write(self, path, lang):
        try:
            with open(pth.ini_file, 'w+', encoding='UTF-8') as settings:
                settings.write('game_location=' + path + '\nlang=' + lang)
        except FileNotFoundError:
            print("\a")
            QMessageBox.about(self, "Warning", "Error")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Controller = Controller()
    # --------Design options------------
    app.setStyle('Fusion')
    app.setStyleSheet(style.main_design)
    # --------Final close func----------
    sys.exit(app.exec())
