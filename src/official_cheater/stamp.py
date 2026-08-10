import pymupdf
import sys
from io import BytesIO
from pathlib import Path
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def _make_transparent_overlay(overlay_file: Path, dpi: int = 150):
    """
    overlay_file: path and filename to a single pdf file that will be the overlay
    we assume it only has one page
    """

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    # open PDF
    doc = pymupdf.open(overlay_file)
    page = doc[0]

    # get render map of PDF
    matrix = pymupdf.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=matrix, alpha=True)

    # build image from map
    img = Image.frombytes(
        "RGBA",
        [pix.width, pix.height],
        pix.samples,
    )

    # get acess to the pixels from the pillow obj
    pixels = img.load()

    # loop through pixels
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]

            # if the fix is white or almost white (anti-aliasing) -
            # make it reansparent ('a' value)
            if r > 250 and g > 250 and b > 250:
                pixels[x, y] = (255, 255, 255, 0)

    # make a byte buffer for the pillow obj
    image_buffer = BytesIO()
    img.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    width = page.rect.width
    height = page.rect.height

    pdf.setPageSize((width, height))
    pdf.drawImage(
        ImageReader(image_buffer),
        0,
        0,
        width=width,
        height=height,
        mask="auto",
    )
    pdf.showPage()

    pdf.save()

    pdf_buffer.seek(0)
    return pdf_buffer


def process_arguements(args) -> None:
    missing_files: list[Path] = []
    error: bool = False

    # make sure all files are accessable
    # base file
    if not args.base.exists():
        missing_files.append(args.base)

    # overlay file(s) for every page
    missing_files.extend(f for f in args.overlay_all if not f.exists())

    # overlay file(s) for the first or last page of an event grouping
    if args.overlay_event is not None:
        missing_files.extend(f for f in args.overlay_event if not f.exists())

    else:
        # 'overlay_event' list is empty, but the flag '--first'/'--last'
        # was found.  These should only be used with an overlay list for events
        if args.event_stamp is not None:
            error = True
            print(
                f"Error: '--{args.event_stamp}' " "found when 'overlay_event' was empty"
            )

    # list any missing files
    if missing_files:
        error = True
        print("Cannot open:", *missing_files, sep=", ")

    if error:
        sys.exit()


def stamp_file(
    base_file: Path,
    overlay_all: list[Path],
    overlay_event_files: list[Path],
    output_file: Path,
) -> None:

    base = PdfReader(base_file)
    writer = PdfWriter()

    # Build the overlay pages once
    overlays: list[PageObject] = []

    for overlay_page in overlay_all:
        print(overlay_page)

        overlay_buffer = _make_transparent_overlay(overlay_page)
        overlay = PdfReader(overlay_buffer)

        overlays.append(overlay.pages[0])

    # Apply ALL overlays to EACH base page
    for page in base.pages:
        for overlay in overlays:
            page.merge_page(overlay)

        writer.add_page(page)

    with open(output_file, "wb") as f:
        writer.write(f)


def run_stamp(args):

    process_arguements(args)

    default_out: str = "_STAMPED"

    # if an output name isn't supplied create default
    # name = base.stem + default_out _ base.suffix(extension)
    if args.output is None:
        # default name = base
        b, e = (args.base.stem, args.base.suffix)

        args.output = Path(f"{b}{default_out}{e}")

    stamp_file(args.base, args.overlay_all, args.overlay_event, args.output)
