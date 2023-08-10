"""
novelWriter – Lorem Ipsum Tool
==============================

File History:
Created: 2022-04-02 [2.0rc1]

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
from __future__ import annotations

import random
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QDialogButtonBox,
    QSpinBox
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import readTextFile
from novelwriter.extensions.switch import NSwitch

logger = logging.getLogger(__name__)


class GuiLipsum(QDialog):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiLipsum")
        self.setObjectName("GuiLipsum")
        if CONFIG.osDarwin:
            self.setWindowFlag(Qt.WindowType.Tool)

        self.mainGui = mainGui

        self.setWindowTitle(self.tr("Insert Placeholder Text"))

        self.innerBox = QHBoxLayout()
        self.innerBox.setSpacing(CONFIG.pxInt(16))

        # Icon
        nPx = CONFIG.pxInt(64)
        vSp = CONFIG.pxInt(4)
        self.docIcon = QLabel()
        self.docIcon.setPixmap(SHARED.theme.getPixmap("proj_document", (nPx, nPx)))

        self.leftBox = QVBoxLayout()
        self.leftBox.setSpacing(vSp)
        self.leftBox.addWidget(self.docIcon)
        self.leftBox.addStretch(1)
        self.innerBox.addLayout(self.leftBox)

        # Form
        self.headLabel = QLabel("<b>{0}</b>".format(self.tr("Insert Lorem Ipsum Text")))

        self.paraLabel = QLabel(self.tr("Number of paragraphs"))
        self.paraCount = QSpinBox()
        self.paraCount.setMinimum(1)
        self.paraCount.setMaximum(100)
        self.paraCount.setValue(5)

        self.randLabel = QLabel(self.tr("Randomise order"))
        self.randSwitch = NSwitch()

        self.formBox = QGridLayout()
        self.formBox.addWidget(self.headLabel, 0, 0, 1, 2, Qt.AlignLeft)
        self.formBox.addWidget(self.paraLabel, 1, 0, 1, 1, Qt.AlignLeft)
        self.formBox.addWidget(self.paraCount, 1, 1, 1, 1, Qt.AlignRight)
        self.formBox.addWidget(self.randLabel, 2, 0, 1, 1, Qt.AlignLeft)
        self.formBox.addWidget(self.randSwitch, 2, 1, 1, 1, Qt.AlignRight)
        self.formBox.setVerticalSpacing(vSp)
        self.formBox.setRowStretch(3, 1)
        self.innerBox.addLayout(self.formBox)

        # Buttons
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.rejected.connect(self._doClose)

        self.btnClose = self.buttonBox.addButton(QDialogButtonBox.Close)
        self.btnClose.setAutoDefault(False)

        self.btnSave = self.buttonBox.addButton(self.tr("Insert"), QDialogButtonBox.ActionRole)
        self.btnSave.clicked.connect(self._doInsert)
        self.btnSave.setAutoDefault(False)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(CONFIG.pxInt(16))
        self.setLayout(self.outerBox)

        logger.debug("Ready: GuiLipsum")

        return

    def __del__(self):  # pragma: no cover
        logger.debug("Delete: GuiLipsum")
        return

    ##
    #  Slots
    ##

    def _doInsert(self):
        """Load the text and insert it in the open document.
        """
        lipsumFile = CONFIG.assetPath("text") / "lipsum.txt"
        lipsumText = readTextFile(lipsumFile).splitlines()

        if self.randSwitch.isChecked():
            random.shuffle(lipsumText)

        pCount = self.paraCount.value()
        inText = "\n\n".join(lipsumText[0:pCount]) + "\n\n"

        self.mainGui.docEditor.insertText(inText)

        return

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
        self.close()
        return

# END Class GuiLipsum
