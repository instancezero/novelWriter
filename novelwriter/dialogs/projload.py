"""
novelWriter – GUI Open Project
==============================
GUI class for the load/browse/new project dialog

File History:
Created: 2020-02-26 [0.4.5]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging

from pathlib import Path
from datetime import datetime

from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QTreeWidget,
    QAbstractItemView, QTreeWidgetItem, QDialogButtonBox, QLabel, QShortcut,
    QFileDialog, QLineEdit
)

from novelwriter import CONFIG
from novelwriter.common import formatInt
from novelwriter.constants import nwFiles

logger = logging.getLogger(__name__)


class GuiProjectLoad(QDialog):

    NONE_STATE = 0
    NEW_STATE  = 1
    OPEN_STATE = 2

    C_NAME  = 0
    C_COUNT = 1
    C_TIME  = 2

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiProjectLoad")
        self.setObjectName("GuiProjectLoad")

        self.mainGui   = mainGui
        self.mainTheme = mainGui.mainTheme
        self.openState = self.NONE_STATE
        self.openPath  = None

        sPx = CONFIG.pxInt(16)
        nPx = CONFIG.pxInt(96)
        iPx = self.mainTheme.baseIconSize

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()
        self.outerBox.setSpacing(sPx)
        self.innerBox.setSpacing(sPx)

        self.setWindowTitle(self.tr("Open Project"))
        self.setMinimumWidth(CONFIG.pxInt(650))
        self.setMinimumHeight(CONFIG.pxInt(400))

        self.nwIcon = QLabel()
        self.nwIcon.setPixmap(self.mainGui.mainTheme.getPixmap("novelwriter", (nPx, nPx)))
        self.innerBox.addWidget(self.nwIcon, 0, Qt.AlignTop)

        self.projectForm = QGridLayout()
        self.projectForm.setContentsMargins(0, 0, 0, 0)

        self.listBox = QTreeWidget()
        self.listBox.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listBox.setColumnCount(3)
        self.listBox.setHeaderLabels([
            self.tr("Working Title"),
            self.tr("Words"),
            self.tr("Last Opened"),
        ])
        self.listBox.setRootIsDecorated(False)
        self.listBox.itemSelectionChanged.connect(self._doSelectRecent)
        self.listBox.itemDoubleClicked.connect(self._doOpenRecent)
        self.listBox.setIconSize(QSize(iPx, iPx))

        treeHead = self.listBox.headerItem()
        treeHead.setTextAlignment(self.C_COUNT, Qt.AlignRight)
        treeHead.setTextAlignment(self.C_TIME, Qt.AlignRight)

        self.lblRecent = QLabel("<b>%s</b>" % self.tr("Recently Opened Projects"))
        self.lblPath = QLabel("<b>%s</b>" % self.tr("Path"))
        self.selPath = QLineEdit("")
        self.selPath.setReadOnly(True)

        self.browseButton = QPushButton("...")
        self.browseButton.setMaximumWidth(int(2.5*self.mainTheme.getTextWidth("...")))
        self.browseButton.clicked.connect(self._doBrowse)

        self.projectForm.addWidget(self.lblRecent,    0, 0, 1, 3)
        self.projectForm.addWidget(self.listBox,      1, 0, 1, 3)
        self.projectForm.addWidget(self.lblPath,      2, 0, 1, 1)
        self.projectForm.addWidget(self.selPath,      2, 1, 1, 1)
        self.projectForm.addWidget(self.browseButton, 2, 2, 1, 1)
        self.projectForm.setColumnStretch(0, 0)
        self.projectForm.setColumnStretch(1, 1)
        self.projectForm.setColumnStretch(2, 0)
        self.projectForm.setVerticalSpacing(CONFIG.pxInt(4))
        self.projectForm.setHorizontalSpacing(CONFIG.pxInt(8))

        self.innerBox.addLayout(self.projectForm)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Open | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doOpenRecent)
        self.buttonBox.rejected.connect(self._doCancel)

        self.newButton = self.buttonBox.addButton(self.tr("New"), QDialogButtonBox.ActionRole)
        self.newButton.clicked.connect(self._doNewProject)

        self.delButton = self.buttonBox.addButton(self.tr("Remove"), QDialogButtonBox.ActionRole)
        self.delButton.clicked.connect(self._doDeleteRecent)

        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        self._populateList()
        self._doSelectRecent()

        keyDelete = QShortcut(self.listBox)
        keyDelete.setKey(QKeySequence(Qt.Key_Delete))
        keyDelete.activated.connect(self._doDeleteRecent)

        logger.debug("Ready: GuiProjectLoad")

        return

    def __del__(self):
        logger.debug("Delete: GuiProjectLoad")
        return

    ##
    #  Buttons
    ##

    def _doOpenRecent(self):
        """Close the dialog window with a recent project selected.
        """
        self._saveSettings()

        self.openPath = None
        self.openState = self.NONE_STATE

        selItems = self.listBox.selectedItems()
        if selItems:
            self.openPath = selItems[0].data(self.C_NAME, Qt.UserRole)
            self.openState = self.OPEN_STATE
            self.accept()

        return

    def _doSelectRecent(self):
        """A recent item has been selected.
        """
        selList = self.listBox.selectedItems()
        if selList:
            self.selPath.setText(selList[0].data(self.C_NAME, Qt.UserRole))
        return

    def _doBrowse(self):
        """Browse for a folder path.
        """
        extFilter = [
            self.tr("novelWriter Project File ({0})").format(nwFiles.PROJ_FILE),
            self.tr("All files ({0})").format("*"),
        ]
        projFile, _ = QFileDialog.getOpenFileName(
            self, self.tr("Open Project"), "", filter=";;".join(extFilter)
        )
        if projFile:
            thePath = Path(projFile).absolute()
            self.selPath.setText(str(thePath))
            self.openPath = thePath
            self.openState = self.OPEN_STATE
            self.accept()

        return

    def _doCancel(self):
        """Close the dialog window without doing anything.
        """
        self.openPath = None
        self.openState = self.NONE_STATE
        self.close()
        return

    def _doNewProject(self):
        """Create a new project.
        """
        self._saveSettings()
        self.openPath = None
        self.openState = self.NEW_STATE
        self.accept()
        return

    def _doDeleteRecent(self):
        """Remove an entry from the recent projects list.
        """
        selList = self.listBox.selectedItems()
        if selList:
            projName = selList[0].text(self.C_NAME)
            msgYes = self.mainGui.askQuestion(
                self.tr("Remove Entry"),
                self.tr(
                    "Remove '{0}' from the recent projects list? "
                    "The project files will not be deleted."
                ).format(projName)
            )
            if msgYes:
                CONFIG.recentProjects.remove(
                    selList[0].data(self.C_NAME, Qt.UserRole)
                )
                self._populateList()

        return

    ##
    #  Events
    ##

    def closeEvent(self, theEvent):
        """Capture the user closing the dialog so we can save settings.
        """
        self._saveSettings()
        theEvent.accept()
        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self):
        """Save the changes made to the dialog.
        """
        colWidths = [0, 0, 0]
        colWidths[self.C_NAME]  = self.listBox.columnWidth(self.C_NAME)
        colWidths[self.C_COUNT] = self.listBox.columnWidth(self.C_COUNT)
        colWidths[self.C_TIME]  = self.listBox.columnWidth(self.C_TIME)
        CONFIG.setProjLoadColWidths(colWidths)
        return

    def _populateList(self):
        """Populate the list box with recent project data.
        """
        self.listBox.clear()
        dataList = CONFIG.recentProjects.listEntries()
        sortList = sorted(dataList, key=lambda x: x[3], reverse=True)
        nwxIcon = self.mainGui.mainTheme.getIcon("proj_nwx")
        for path, title, words, time in sortList:
            newItem = QTreeWidgetItem([""]*4)
            newItem.setIcon(self.C_NAME, nwxIcon)
            newItem.setText(self.C_NAME, title)
            newItem.setData(self.C_NAME, Qt.UserRole, path)
            newItem.setText(self.C_COUNT, formatInt(words))
            newItem.setText(self.C_TIME, datetime.fromtimestamp(time).strftime("%x %X"))
            newItem.setTextAlignment(self.C_NAME,  Qt.AlignLeft  | Qt.AlignVCenter)
            newItem.setTextAlignment(self.C_COUNT, Qt.AlignRight | Qt.AlignVCenter)
            newItem.setTextAlignment(self.C_TIME,  Qt.AlignRight | Qt.AlignVCenter)
            newItem.setFont(self.C_TIME, self.mainTheme.guiFontFixed)
            self.listBox.addTopLevelItem(newItem)

        if self.listBox.topLevelItemCount() > 0:
            self.listBox.topLevelItem(0).setSelected(True)

        projColWidth = CONFIG.projLoadColWidths
        if len(projColWidth) == 3:
            self.listBox.setColumnWidth(self.C_NAME,  projColWidth[self.C_NAME])
            self.listBox.setColumnWidth(self.C_COUNT, projColWidth[self.C_COUNT])
            self.listBox.setColumnWidth(self.C_TIME,  projColWidth[self.C_TIME])

        return

# END Class GuiProjectLoad
