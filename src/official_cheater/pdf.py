import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def merge_pdfs(pdfs: list[Path], output: Path) -> None:
    """Merge PDFs in order into a single PDF."""
    writer = PdfWriter()

    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            writer.add_page(page)

    try:
        with output.open("wb") as f:
            writer.write(f)
    except OSError as exc:
        print(f"ERROR: cannot write '{output}': {exc.strerror}")
        sys.exit(1)


_PDF_EX: str = ".pdf"


def process_arguements(args) -> list[Path]:
    """Process command-line arguments for the 'pdf' option.

    Args:
        args: Command-line arguments. See __cli__.py for the current list
            of arguments and their types.
    """
    pdfs: list[Path] = []

    for path in args.merge:
        if path.is_file() and path.suffix.casefold() == _PDF_EX:
            pdfs.append(path)

        elif path.is_dir():        
            if args.recursive:            
                pdfs.extend(
                    p
                    for p in path.rglob("*")
                    if p.is_file() and p.suffix.casefold() == _PDF_EX
                )
                
            else:
                pdfs.extend(
                    p
                    for p in path.glob("*")
                    if p.is_file() and p.suffix.casefold() == _PDF_EX
                )

    return pdfs


def run_pdf(args) -> None:

    all_files: list[Path] = process_arguements(args)

    # if we couldn't find any files - exit out
    if not all_files:
        sys.exit(1)

    # if an output name isn't supplied create default
    # name = all_files[0] dir = merged_files.pdf
    if args.output is None:
        args.output = Path(f"{all_files[0].parent}\\files_MERGED.pdf")

    merge_pdfs(all_files, args.output)
    
    print(f"MERGED: {args.output}")
