import shutil
import sys
from pathlib import Path

import pytest

from official_cheater.cli import main


def delete_merged_pdfs(directory: str) -> None:
    for pdf in Path(directory).rglob("*_MERGED.pdf"):
        if pdf.is_file():
            pdf.unlink()


def save_merged_pdfs(find_dir: str, save_dir: str) -> None:
    source_dir = Path(find_dir)
    output_dir = Path(save_dir)

    for pdf in source_dir.rglob("*_MERGED.pdf"):
        if pdf.is_file() and output_dir not in pdf.parents:
            shutil.move(pdf, output_dir / pdf.name)


def test_001(monkeypatch, request):
    """merge two files - same directory - default name"""
    delete_merged_pdfs(r".\test")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "pdf",
            "--merge",
            r".\tests\pdf_test\0.pdf",
            r".\tests\pdf_test\6.pdf",
        ],
    )

    main()


def test_002(monkeypatch, request):
    """merge two files - same directory - named"""
    func_name = request.node.name

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "pdf",
            "--merge",
            r".\tests\pdf_test\0.pdf",
            r".\tests\pdf_test\6.pdf",
            "--output",
            rf".\tests\{func_name}_two_files_same_dir_MERGED.pdf",
        ],
    )

    main()


def test_003(monkeypatch, request):
    """merge two files - different directory - named"""
    func_name = request.node.name

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "pdf",
            "--merge",
            r".\tests\pdf_test\0.pdf",
            r".\tests\pdf_test\level_\2.pdf",
            "--output",
            rf".\tests\{func_name}_two_files_diff_dir_MERGED.pdf",
        ],
    )

    main()


def test_004(monkeypatch, request):
    """merge dir - non-recursive - named"""
    func_name = request.node.name

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "pdf",
            "--merge",
            r".\tests\pdf_test",
            "--output",
            rf".\tests\{func_name}_dir_non-recursive_MERGED.pdf",
        ],
    )

    main()


def test_005(monkeypatch, request):
    """merge a file and a dir non-recursive - named"""
    func_name = request.node.name

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "pdf",
            "--merge",
            r".\tests\pdf_test\0.pdf",
            r".\tests\pdf_test\level_1\level_2",
            "--output",
            rf".\tests\{func_name}_file and dir_non-recursive_MERGED.pdf",
        ],
    )

    main()


def test_006(monkeypatch, request):
    """merge a file and a dir recursive - named"""
    func_name = request.node.name

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "pdf",
            "--merge",
            r".\tests\pdf_test\0.pdf",
            r".\tests\pdf_test\level_1\level_2",
            "--recursive",
            "--output",
            rf".\tests\{func_name}_file and dir_recursive_MERGED.pdf",
        ],
    )

    main()


def test_007(monkeypatch, request):
    """merge dir - recursive - named"""
    func_name = request.node.name

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "pdf",
            "--merge",
            r".\tests\pdf_test",
            "--recursive",
            "--output",
            rf".\tests\{func_name}_dir_recursive_MERGED.pdf",
        ],
    )

    main()


def test_error_001(monkeypatch, request):
    """Named output file is already opened"""
    func_name = request.node.name
    out_file = rf".\tests\{func_name}_dir_recursive_MERGED.pdf"

    monkeypatch.setattr(
        Path,
        "open",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            PermissionError(13, "Permission denied", out_file)
        ),
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "pdf",
            "--merge",
            r".\tests\pdf_test\level_1\level_2",
            "--output",
            out_file,
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1


def test_error_002(monkeypatch, request):
    """No mergeable PDFs are found given the --merge input"""
    func_name = request.node.name

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "pdf",
            "--merge",
            r".\tests\pdf_test\level_1\level_2\empty",
            "--output",
            rf".\tests\{func_name}_dir_recursive_MERGED.pdf",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
