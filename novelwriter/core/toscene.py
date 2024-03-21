"""
novelWriter – Scene Structure Exporter
======================================

File History:
Created: 2024-03-17 ToScene

This file is a part of novelWriter
Copyright 2024, Alan Langford

Based on work
Copyright 2018–2024, Veronica Berglyd Olsen

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

import json
import logging

from time import time
from pathlib import Path
from typing import List, Dict, Any

from novelwriter import CONFIG
from novelwriter.common import formatTimeStamp
from novelwriter.constants import nwHeadFmt, nwKeyWords, nwLabels, nwHtmlUnicode
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import Tokenizer, stripEscape

logger = logging.getLogger(__name__)


class ToScene(Tokenizer):
    """Core: Scene Document Writer

    Extend the Tokenizer class to write scene structure in CSV and JSON formats
    """

    def __init__(self, project: NWProject) -> None:
        super().__init__(project)

        self._blankScene = {
            "name": "",
            "plot": "",
            "synopsis": "",
            "incite": "",
            "complication": "",
            "turning": "",
            "crisis": "",
            "climax": "",
            "resolution": "",
            "shift": "",
            "polarity": "",
            "pov": "",
            "focus": "",
            "time": "",
            "duration": "",
            "location": "",
            "char": "",
            "objects": "",
            "custom": "",
            "comments": "",
        }
        self._sceneData = {}
        self._inScene = False
        self._populated = {}
        for key in self._blankScene:
            self._populated[key] = False
        self._fullDoc = [{
            "name": "Scene Name",
            "plot": "Plot Name",
            "synopsis": "Synopsis",
            "incite": "Inciting Incident",
            "complication": "Complication",
            "turning": "Turning Point",
            "crisis": "Crisis",
            "climax": "Climax",
            "resolution": "(Non)-Resolution",
            "shift": "Value shift",
            "polarity": "Polarity Shift",
            "pov": "Point of View",
            "focus": "Focus Character",
            "time": "Timeline(s)",
            "duration": "Scene Duration",
            "location": "Location",
            "char": "Character(s)",
            "objects": "Objects",
            "custom": "Custom Data",
            "comments": "Comments",
        }]

        return

    ##
    #  Properties
    ##

    @property
    def fullDocument(self) -> list[dict[str | Any, str | Any]]:
        return self._fullDoc

    ##
    #  Class Methods
    ##

    def getFullResultSize(self) -> int:
        """Return the size of the full result."""
        return sum(len(x) for x in self._fullDoc)

    def doConvert(self) -> None:
        """Build scene structures."""

        for tType, nHead, tText, tFormat, tStyle in self._tokens:

            if tType == self.T_HEAD3:
                if self._inScene:
                    self._fullDoc.append(self._sceneData)
                    self._sceneData = {}

                self._sceneData["name"] = tText
                self._populated["name"] = True
                self._inScene = True

            elif tType == self.T_SYNOPSIS:
                self._sceneData["synopsis"] = tText
                self._populated["synopsis"] = True

            elif tType == self.T_CLIMAX:
                self._sceneData["climax"] = tText
                self._populated["climax"] = True

            elif tType == self.T_COMPLICATION:
                self._sceneData["complication"] = tText
                self._populated["complication"] = True

            elif tType == self.T_DURATION:
                self._sceneData["duration"] = tText
                self._populated["duration"] = True

            elif tType == self.T_INCITE:
                self._sceneData["incite"] = tText
                self._populated["incite"] = True

            elif tType == self.T_POLARITY:
                self._sceneData["polarity"] = tText
                self._populated["polarity"] = True

            elif tType == self.T_RESOLUTION:
                self._sceneData["resolution"] = tText
                self._populated["resolution"] = True

            elif tType == self.T_SHIFT:
                self._sceneData["shift"] = tText
                self._populated["shift"] = True

            elif tType == self.T_TURNING:
                self._sceneData["turning"] = tText
                self._populated["turning"] = True

            elif tType == self.T_WHEN:
                self._sceneData["when"] = tText
                self._populated["when"] = True

            elif tType == self.T_COMMENT:
                if "comments" in self._sceneData:
                    self._sceneData["comments"] = self._sceneData["comments"] + " " + tText
                else:
                    self._sceneData["comments"] = tText
                self._populated["comments"] = True

            elif tType == self.T_KEYWORD:
                # self.T_KEYWORD, nHead, aLine[1:].strip(), [], sAlign
                valid, bits, _ = self._project.index.scanThis("@"+tText)
                if valid and bits and bits[0] in nwLabels.KEY_NAME:
                    slot = bits[0][1:]
                    self._sceneData[slot] = "\n".join(bits[1:])
                    self._populated[slot] = True
        return

    def saveCSV(self, path: str | Path) -> None:
        """Save the data to a CSV file."""
        if len(self._sceneData):
            self._fullDoc.append(self._sceneData)
        with open(path, mode="w", encoding="utf-8") as fObj:
            for scene in self._fullDoc:
                buffer = []
                for key in self._blankScene:
                    if self._populated[key]:
                        if key in scene:
                            buffer.append("\"" + scene[key].replace("\"", "\\\"") + "\"")
                        else:
                            buffer.append("\"\"")

                fObj.write(",".join(buffer) + "\n")
        logger.info("Wrote file: %s", path)
        return

    def saveJson(self, path: str | Path) -> None:
        """Save the data to a JSON file."""
        if len(self._sceneData):
            self._fullDoc.append(self._sceneData)
        timeStamp = time()
        data = {
            "meta": {
                "projectName": self._project.data.name,
                "novelAuthor": self._project.data.author,
                "buildTime": int(timeStamp),
                "buildTimeStr": formatTimeStamp(timeStamp),
            },
            "structure": self._fullDoc[1:],
        }
        with open(path, mode="w", encoding="utf-8") as fObj:
            json.dump(data, fObj, indent=2)
        logger.info("Wrote file: %s", path)
        return

    def replaceTabs(self, nSpaces: int = 8, spaceChar: str = "&nbsp;") -> None:
        """Replace tabs with spaces."""
        for scene in self._fullDoc:
            for key in scene:
                scene[key] = scene[key].replace("\t", " ")

        return

# END Class ToHtml
