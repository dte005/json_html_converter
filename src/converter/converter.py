from pathlib import Path

from converter.lib.html_minifier import HtmlMinifier
from converter.lib.html_reader import HtmlReader
from converter.lib.image_encoder import ImageEncoder
from converter.lib.json_writer import JsonWriter
from converter.lib.section_extractor import SectionExtractor


class Converter:
    def __init__(self, input_dir: Path, output_dir: Path) -> None:
        self._input_dir = input_dir
        self._output_dir = output_dir

    def run(self) -> list[Path]:
        return [self._convert_file(html_path) for html_path in sorted(self._input_dir.glob("*.html"))]

    def _convert_file(self, html_path: Path) -> Path:
        soup = HtmlReader(html_path).parse()
        document = SectionExtractor(soup).extract()

        minifier = HtmlMinifier()
        for section in document.sections:
            section.content_html = minifier.minify(section.content_html)

        image_encoder = ImageEncoder(html_path)
        output_path = self._output_dir / f"{html_path.stem}.json"
        JsonWriter(image_encoder).write(document, output_path)
        return output_path
