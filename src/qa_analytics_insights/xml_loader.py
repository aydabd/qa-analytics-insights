"""Copyright (c) 2023, Aydin Abdi.

This module is responsible for loading XML files.
"""

from __future__ import annotations

from typing import Optional
from xml.etree import ElementTree as ET


class XMLLoader:
    """Responsible for loading XML file."""

    def __init__(self, xml_path: str) -> None:
        """Responsible for loading XML files into XMLParser.

        Args:
            xml_path: Path to the XML file.
        """
        self.xml_path = xml_path
        self._tree: Optional[ET.ElementTree[ET.Element]] = None
        self._root: Optional[ET.Element] = None

    def load(self) -> ET.Element:  # pragma: no cover - simple file loading
        """Load the XML file and return the root element."""
        self._tree = ET.parse(self.xml_path)
        self._root = self._tree.getroot()
        return self._root

    @property
    def tree(self) -> ET.ElementTree[ET.Element]:  # pragma: no cover
        """Returns the XML tree.

        Returns:
            XML tree.
        """
        if not self._tree:  # pragma: no cover
            self._tree = ET.parse(self.xml_path)
        # Type assertion to help mypy understand we've checked the optional
        assert self._tree is not None
        return self._tree

    @property
    def root(self) -> ET.Element:  # pragma: no cover
        """Returns the XML root.

        Returns:
            XML root.
        """
        if not self._root:  # pragma: no cover
            self._root = self.tree.getroot()
        # Type assertion to help mypy understand we've checked the optional
        assert self._root is not None
        return self._root
