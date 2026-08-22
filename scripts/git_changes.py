import argparse
import subprocess
from pathlib import Path


def get_changed_files(repo: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )

    files = []

    for line in result.stdout.splitlines():
        if not line:
            continue

        # First two characters are the Git status codes.
        filename = line[3:]

        files.append(repo / filename)

    return files


SEPARATOR = "=" * 80


def combine_files(repo: Path, output: Path) -> None:
    files = get_changed_files(repo)

    with output.open("w", encoding="utf-8") as combined:
        for file in files:
            relative = file.relative_to(repo)

            combined.write(f"\n{SEPARATOR}\n")
            combined.write(f"FILE: {relative}\n")
            combined.write(f"{SEPARATOR}\n\n")

            combined.write(file.read_text(encoding="utf-8"))
            combined.write("\n")


def split_combined_file(combined: Path, repo: Path) -> None:
    text = combined.read_text(encoding="utf-8")

    marker = SEPARATOR + "\nFILE: "

    sections = text.split(marker)

    for section in sections[1:]:
        relative, content = section.split(
            "\n" + SEPARATOR + "\n\n",
            maxsplit=1,
        )

        output = repo / relative

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content.rstrip("\n") + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="git git'r")
    parser.add_argument("location", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--zip", type=Path)
    group.add_argument("--unzip", type=Path)
    args = parser.parse_args()

    if args.zip:
        combine_files(args.location, args.zip)
    elif args.unzip:
        split_combined_file(args.unzip, args.location)
