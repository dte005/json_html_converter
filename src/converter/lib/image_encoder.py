import base64
import mimetypes
from pathlib import Path


class ImageEncoder:
    def __init__(self, html_path: Path) -> None:
        self._base_dir = html_path.parent
        self._stem = html_path.stem

    def encode(self, src: str) -> dict:
        filename = Path(src).name
        mime_type = mimetypes.guess_type(filename)[0]
        resolved = self._resolve(src, filename)
        if resolved is None:
            return {"filename": filename, "mime_type": mime_type, "base64": None}
        encoded = base64.b64encode(resolved.read_bytes()).decode("ascii")
        return {"filename": filename, "mime_type": mime_type, "base64": encoded}

    def _resolve(self, src: str, filename: str) -> Path | None:
        candidates = [
            self._base_dir / src,
            self._base_dir / "files" / filename,
            self._base_dir / f"{self._stem}_files" / filename,
        ]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        for match in self._base_dir.rglob(filename):
            if match.is_file():
                return match
        return None
