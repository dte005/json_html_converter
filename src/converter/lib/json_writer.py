import json
from pathlib import Path

from converter.lib.image_encoder import ImageEncoder
from converter.lib.section_extractor import ExtractedDocument, ExtractedSection


class JsonWriter:
    def __init__(self, image_encoder: ImageEncoder) -> None:
        self._image_encoder = image_encoder

    def build(self, document: ExtractedDocument) -> dict:
        return {
            "header": document.header,
            "sections": [self._build_section(section) for section in document.sections],
            "approvals": document.approvals,
            "attachments": [self._image_encoder.encode(src) for src in document.header_images],
        }

    def _build_section(self, section: ExtractedSection) -> dict:
        return {
            "id": section.id,
            "title": section.title,
            "content": section.content_html,
            "attachments": [self._image_encoder.encode(src) for src in section.images],
        }

    def write(self, document: ExtractedDocument, output_path: Path) -> None:
        data = self.build(document)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
