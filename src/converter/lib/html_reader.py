from pathlib import Path

from bs4 import BeautifulSoup


class HtmlReader:
    def __init__(self, html_path: Path) -> None:
        self._html_path = html_path

    def parse(self) -> BeautifulSoup:
        content = self._html_path.read_text(encoding="utf-8")
        return BeautifulSoup(content, "html.parser")
