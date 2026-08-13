from pathlib import Path

from converter import Converter


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    Converter(repo_root / "input", repo_root / "output").run()


if __name__ == "__main__":
    main()
