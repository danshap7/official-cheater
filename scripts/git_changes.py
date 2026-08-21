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


def combine_files(repo: Path, output: Path) -> None:
    files = get_changed_files(repo)

    with output.open("w", encoding="utf-8") as combined:
        for file in files:
            relative = file.relative_to(repo)

            combined.write(f"\n{'=' * 80}\n")
            combined.write(f"FILE: {relative}\n")
            combined.write(f"{'=' * 80}\n\n")

            combined.write(file.read_text(encoding="utf-8"))
            combined.write("\n")


if __name__ == "__main__":
    repo = Path(".")
    combine_files(repo, Path("changed_files.txt"))
