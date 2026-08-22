import sys
from pathlib import Path

TEXT_EXTENSIONS = {
    ".py",
    ".pyi",
    ".toml",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
}


def clean_directory(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        text = path.read_text(encoding="utf-8")

        cleaned = "\n".join(line.rstrip() for line in text.splitlines())

        if text.endswith("\n"):
            cleaned += "\n"

        if cleaned != text:
            path.write_text(cleaned, encoding="utf-8")
            print(path)


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    clean_directory(root)
