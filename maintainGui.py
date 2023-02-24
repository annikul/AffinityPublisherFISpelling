# APPLICATION FOR MAINTAINING SPELLING DICTIONARY
# ===============================================

# LIBRARIES AND MODULES
# ---------------------

import sys  # For accessing system parameters
import os  # For file path handling
from PyQt6 import QtWidgets  # For the Qt functionality
from PyQt6.QtGui import QDesktopServices  # To show web pages
from PyQt6.QtCore import QUrl  # For defining the URL of a web page to open
from PyQt6.uic import loadUi  # For loading the UI file
from qt_material import QtStyleTools, apply_stylesheet  # For theme adjustments
import dialogs # Internal module for dialogs
import dictionaryMaintain # Internal module for dictionary maintenance


# CLASS DEFINITIONS
# -----------------

# The main window, inherits also QtStyleTools for theming the UI
class MainWindow(QtWidgets.QMainWindow, QtStyleTools):
    """Creates a main window"""

    # Constructor
    def __init__(self):
        super().__init__()

        # Create the main window using the latest custom theme
        self.main = loadUi('MainWindow.ui', self)
        self.setWindowTitle('Sanakirjan ylläpito')

        # Create and set the window icon (check mark)
        # MEMO muista StandardPixmap jos ope käyttää PyQt5 ja sä PyQt6
        iconPixmap = QtWidgets.QStyle.StandardPixmap.SP_DialogApplyButton
        icon = self.style().standardIcon(iconPixmap)
        self.setWindowIcon(icon)

        # Load settings from json file
        self.settings = dialogs.settingsFromJsonFile('settings.json')
        scale = self.settings['scale']
        self.extra = {'density_scale': f'{scale}'}

        # Use latest chosen theme
        apply_stylesheet(
            self.main, theme=self.settings['theme'], extra=self.extra)

        # MENU ACTIONS

        # Open the settings
        self.actionDictionaryFolder.triggered.connect(self.openSettings)

        # Set the dark theme
        self.actionDark.triggered.connect(self.setDarkTheme)

        # Set the light theme
        self.actionLight.triggered.connect(self.setLightTheme)

        # Set the default theme
        self.actionDefaultTheme.triggered.connect(self.setDefaultTheme)

        # Set a custon theme
        self.actionAdjustTheme.triggered.connect(self.setCustomTheme)

        # Set the size of UI elements
        self.actionSize.triggered.connect(self.changeElementSize)

        # Open Huolla sanakirjaa... dialog
        self.actionSanityCheck.triggered.connect(self.sanityCheck)

        # Open Lisää Joukahaisesta... dialog
        self.actionAddFromJoukahainen.triggered.connect(
            self.bringFromJoukahainen)

        # Open Help in the default browser
        self.actionWikiPage.triggered.connect(self.openWiki)
        
        # PUSH BUTTONS

        # Tallenna kaikki push button, adds all words to the dictionary file
        self.saveAllPB = self.addAllPushButton
        self.saveAllPB.setEnabled(False)
        self.saveAllPB.clicked.connect(self.saveAll)

        # Tallenna valitut push button, adds selected words to the dictionary file
        self.saveSelectedPB = self.addChosenPushButton
        self.saveSelectedPB.setEnabled(False)
        self.saveSelectedPB.clicked.connect(self.saveSelected)

        # INPUTS & OUTPUTS

        # A line edit for a new word
        self.wordInput = self.wordToAddLineEdit
        self.wordInput.returnPressed.connect(self.addToList)

        # A list of words to be saved into the spelling dictionary
        self.wordsList = self.wordsListWidget
        self.wordsList.itemDoubleClicked.connect(self.wordsListEdit)
        self.wordsList.itemSelectionChanged.connect(self.enableSaveSelectedPB)

    # A method to open the settings dialog
    def openSettings(self):
        settingsHandler = dialogs.SettingsHandler()
        settingsHandler.exec()

    # A method to apply the dark theme
    def setDarkTheme(self):
        self.settings = dialogs.settingsFromJsonFile('settings.json')
        scale = self.settings['scale']
        self.extra = {'density_scale': f'{scale}'}
        apply_stylesheet(self.main, theme='dark_amber.xml', extra=self.extra)
        self.settings['theme'] = 'dark_amber.xml'
        dialogs.saveSettingsToJsonFile('settings.json', self.settings)

    # A method to apply the light theme
    def setLightTheme(self):
        self.settings = dialogs.settingsFromJsonFile('settings.json')
        scale = self.settings['scale']
        self.extra = {'density_scale': f'{scale}'}
        apply_stylesheet(
            self.main, theme='light_cyan_500.xml', extra=self.extra)
        self.settings['theme'] = 'light_cyan_500.xml'
        dialogs.saveSettingsToJsonFile('settings.json', self.settings)

    # A method to apply the factory default theme (dark one)
    def setDefaultTheme(self):
        self.settings = dialogs.settingsFromJsonFile('settings.json')
        scale = self.settings['scale']
        self.extra = {'density_scale': f'{scale}'}
        apply_stylesheet(self.main, theme='default_theme.xml',
                         extra=self.extra)
        self.settings['theme'] = 'default_theme.xml'
        dialogs.saveSettingsToJsonFile('settings.json', self.settings)

    # A method to open custom theme tools
    def setCustomTheme(self):
        self.settings = dialogs.settingsFromJsonFile('settings.json')
        scale = self.settings['scale']
        self.extra = {'density_scale': f'{scale}'}
        self.show_dock_theme(self.main)
        self.settings['theme'] = 'my_theme.xml'
        dialogs.saveSettingsToJsonFile('settings.json', self.settings)

    # A method for sizing UI texts and other UI elements
    def changeElementSize(self):
        setSize = dialogs.SetSize()
        setSize.exec()
        self.settings = dialogs.settingsFromJsonFile('settings.json')
        scale = self.settings['scale']
        self.extra = {'density_scale': f'{scale}'}
        apply_stylesheet(
            self.main, theme=self.settings['theme'], extra=self.extra)

    # A method to send word from the line edit to the word list
    def addToList(self):
        item = self.wordInput.text().strip()  # Clean white spaces
        if item != '':
            self.wordsList.addItem(item)
            self.wordInput.clear()
            self.enableSaveAll()

    # A method for editing a word in the list of words
    def wordsListEdit(self, item):
        row = self.wordsList.row(item)
        toBeEdited = self.wordsList.takeItem(row)
        self.wordInput.setText(toBeEdited.text())
        self.enableSaveAll()

    # A method to save selected words into the spelling dictionary
    def saveSelected(self):
        selectedItems = self.wordsList.selectedItems()
        addList = []
        for item in selectedItems:
            row = self.wordsList.row(item)
            addList.append(item.text())
            self.wordsList.takeItem(row)
        self.saveSelectedPB.setEnabled(False)
        currentSettings = dialogs.settingsFromJsonFile('settings.json')
        dictionaryFile = currentSettings['dictionary']
        encoding = currentSettings['encoding']
        maintenanceOperation = dictionaryMaintain.MaintenanceOperation(
            dictionaryFile, encoding)
        result = maintenanceOperation.addSeveralWordsToDictionaryFile(addList)

    # A method to save all words into the spelling dictionary
    def saveAll(self):
        addList = []
        count = self.wordsList.count()
        for row in range(count):
            addList.append(self.wordsList.item(row).text())
        self.wordsList.clear()
        currentSettings = dialogs.settingsFromJsonFile('settings.json')
        dictionaryFile = currentSettings['dictionary']
        encoding = currentSettings['encoding']
        maintenanceOperation = dictionaryMaintain.MaintenanceOperation(
            dictionaryFile, encoding)
        maintenanceOperation.addSeveralWordsToDictionaryFile(addList)
        self.saveAllPB.setEnabled(False)

    # A method to enable and disable Tallenna kaikki push button
    def enableSaveAll(self):
        count = self.wordsList.count()
        if count > 0:
            self.saveAllPB.setEnabled(True)
        else:
            self.saveAllPB.setEnabled(False)

    # A method to enable and disable Tallenna valitut push button
    def enableSaveSelectedPB(self):
        selections = len(self.wordsList.selectedItems())
        if selections > 0:
            self.saveSelectedPB.setEnabled(True)
        else:
            self.saveSelectedPB.setEnabled(False)

    # A method to open the dictionary sanitizing dialog
    def sanityCheck(self):
        sanitizeDictionary = dialogs.SanitizeDictionary()
        sanitizeDictionary.exec()

    # A Method to open dialog for importing words from Joukahainen xml dictionary
    def bringFromJoukahainen(self):
        joukahainenDialog = dialogs.JoukahainenDialog()
        joukahainenDialog.exec()

    # A method for opening Help page in Github Wiki
    def openWiki(self):
        url = QUrl(
            'https://github.com/MikaVainio/AffinityPublisherFISpelling/wiki/Ohje-suomeksi')
        QDesktopServices.openUrl(url)


if __name__ == "__main__":

    # Create the application
    app = QtWidgets.QApplication(sys.argv)

    # Create the Main Window object from MainWindow class and show it on the screen
    appWindow = MainWindow()
    appWindow.main.show()
    sys.exit(app.exec())
