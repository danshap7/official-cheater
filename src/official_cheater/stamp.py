"""Handles the 'stamp' options for the official-cheater tools."""

import os
import sys
from io import BytesIO
from pathlib import Path

import pymupdf
from PIL import Image, ImageChops
from pypdf import PageObject, PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from official_cheater import report


def _make_transparent_overlay(overlay_file: Path, dpi: int = 150) -> BytesIO:
    """Return a buffer containing a transparent version of the supplied PDF.

    Args:
        overlay_file: Path to the overlay PDF.
        dpi: Dots per inch used by the imaging code.

    Returns:
        A BytesIO buffer containing the transparent PDF.
    """
    # Create an in-memory PDF for the processed overlay.
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    # Open the source PDF. We only use the first page as the overlay.
    with pymupdf.open(overlay_file) as doc:
        page = doc[0]

        # Render the PDF page to an image at the requested DPI.
        # 72 DPI is the native PDF resolution, so scale accordingly.
        matrix = pymupdf.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=matrix, alpha=True)

        # Convert the PyMuPDF pixel data into a Pillow RGBA image.
        img = Image.frombytes(
            "RGBA",
            (pix.width, pix.height),
            pix.samples,
        )

        # Create a lookup table that converts each color value to
        # either opaque (255) or transparent (0).
        #
        # Values 0-250  -> opaque
        # Values 251-255 -> transparent
        lut = [255] * 251 + [0] * 5

        # Separate the image into its individual color channels.
        r, g, b, _ = img.split()

        # Apply the lookup table to each color channel.
        r_mask = r.point(lut)
        g_mask = g.point(lut)
        b_mask = b.point(lut)

        # A pixel should only be transparent when ALL three color
        # channels are greater than 250.
        #
        # darker() effectively performs a minimum operation, so
        # a pixel remains opaque if any channel is <= 250.
        alpha = ImageChops.darker(
            r_mask,
            ImageChops.darker(g_mask, b_mask),
        )

        # Replace the image's alpha channel with our transparency mask.
        img.putalpha(alpha)

        # Save the processed image to an in-memory PNG.
        image_buffer = BytesIO()
        img.save(image_buffer, format="PNG")
        image_buffer.seek(0)

        # Use the original PDF dimensions for the output page.
        # These are in PDF points (1/72 inch), independent of the
        # DPI used to render the image.
        width = page.rect.width
        height = page.rect.height

        pdf.setPageSize((width, height))

        # Put the transparent PNG back onto the PDF page.
        pdf.drawImage(
            ImageReader(image_buffer),
            0,
            0,
            width=width,
            height=height,
            mask="auto",
        )

        pdf.showPage()

    # Finish writing the PDF.
    pdf.save()

    # Rewind the buffer so the caller can read it from the beginning.
    pdf_buffer.seek(0)

    return pdf_buffer


def _get_overlay_transparencies(pages: list[Path]) -> list[PageObject]:
    """Return a list of transparent PDF pages based on the supplied PDF files.

    Args:
        pages: Paths to the PDF files.

    Returns:
        A list of PDF PageObjects.
    """
    overlays: list[PageObject] = []
    if pages is not None:
        for page in pages:
            overlay_buffer = _make_transparent_overlay(page)
            overlay = PdfReader(overlay_buffer)

            overlays.append(overlay.pages[0])

    return overlays


def _get_event_stamp_page(
    meet_program: Path, stamp_first_page: bool = True
) -> list[int]:
    """Return a list containing one item per page.

    Each page that should be stamped contains the event number. Pages that
    should not be stamped contain 0.

    Args:
        meet_program: Path to the PDF meet program. The program should contain
            a single column with one page per event.
        stamp_first_page: If True, stamp the first page of a multi-page event.
            If False, stamp the last page of the multi-page event.

    Returns:
        A list mapping each page to its event number, or 0 if the page should
        not be stamped.
    """
    ev_mapping: dict[int, list[int]] = report.get_event_page_mapping(meet_program)

    page_count = sum(len(values) for values in ev_mapping.values())

    result: list[int] = [0] * page_count

    for key, values in ev_mapping.items():
        index = values[0] if stamp_first_page else values[-1]
        result[index] = key

    return result


def stamp_file(
    base_file: Path,
    overlay_all: list[Path],
    overlay_event: list[Path],
    first_page_event: bool,
    output_file: Path,
) -> None:
    """Create a file containing overlays applied to a base PDF file.

    Args:
        base_file: Main PDF file to which the overlays are applied.
        overlay_all: List of overlay files applied to every page in the
            base file. Each overlay file can contain only one page.
        overlay_event: List of overlay files applied once per event in
            the base file. Each overlay file can contain only one page.
        first_page_event: If True, apply event overlays to the first page
            of each event. If False, apply them to the last page.
        output_file: Output file where the overlaid PDF is written.
    """
    writer = PdfWriter(clone_from=base_file)

    all_overlays = _get_overlay_transparencies(overlay_all)
    ev_overlays = _get_overlay_transparencies(overlay_event)

    stamped_ev = _get_event_stamp_page(base_file, first_page_event)

    for i, page in enumerate(writer.pages):
        for overlay in all_overlays:
            page.merge_page(overlay)

        if stamped_ev[i] > 0:
            for overlay in ev_overlays:
                page.merge_page(overlay)

    with output_file.open("wb") as f:
        writer.write(f)


def process_arguements(args) -> None:
    """Process command-line arguments for the 'stamp' option.

    Args:
        args: Command-line arguments. See __cli__.py for the current list
            of arguments and their types.
    """
    missing_files: list[Path] = []
    error: bool = False

    # make sure all files are accessable
    # base file
    if not args.base_file.exists():
        missing_files.append(args.base_file)

    # overlay file(s) for every page
    if args.overlay_all is not None:
        missing_files.extend(f for f in args.overlay_all if not f.exists())

    # overlay file(s) for the first or last page of an event grouping
    if args.overlay_event is not None:
        missing_files.extend(f for f in args.overlay_event if not f.exists())

    else:
        # 'overlay_event' list is empty, but the flag '--first'/'--last'
        # was found.  These should only be used with an overlay list for events
        if args.event_stamp is not None:
            error = True
            print(f"Error: '--{args.event_stamp}' found when 'overlay_event' was empty")

    # list any missing files
    if missing_files:
        error = True
        print("Cannot open:", *missing_files, sep=", ")

    if error:
        sys.exit(1)


def run_stamp(args) -> None:
    """Runs the stamp tool based on command-line arguments.

    Args:
        args: Command-line arguments. See __cli__.py for the current list
            of arguments and their types.
    """
    print(args) if args.debug else None
    process_arguements(args)

    base: Path = args.base_file

    default_out: str = "_STAMPED"

    # if an output name isn't supplied create default
    # name = base.stem + default_out _ base.suffix(extension)
    if args.output is None:
        args.output = Path(f"{base.parent}\\{base.stem}{default_out}{base.suffix}")

    stamp_first: bool = args.event_stamp == "first"

    stamp_file(
        args.base_file, args.overlay_all, args.overlay_event, stamp_first, args.output
    )

    if args.print:
        os.startfile(str(args.output), "print")
