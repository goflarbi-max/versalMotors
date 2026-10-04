"""Small, deterministic PDF exporters used by Streamlit download buttons."""

import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos


def _pdf_text(value: object) -> str:
    """Return text supported by the built-in PDF font without raising errors."""
    return str(value).encode("latin-1", "replace").decode("latin-1")


def _line(pdf: FPDF, height: float, value: object) -> None:
    """Write a wrapped line and reset the cursor to the left margin."""
    pdf.multi_cell(
        0, height, _pdf_text(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )


def text_to_pdf(title: str, body: str) -> bytes:
    """Render a titled plain-text report as a valid PDF byte stream."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    _line(pdf, 8, title)
    pdf.ln(2)
    pdf.set_font("Helvetica", size=10)
    for line in body.splitlines():
        _line(pdf, 6, line or " ")
    return bytes(pdf.output())


def dataframe_to_pdf(title: str, frame: pd.DataFrame) -> bytes:
    """Render dataframe records in a narrow, mobile-friendly report layout."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    _line(pdf, 8, title)
    pdf.ln(2)

    if frame.empty:
        pdf.set_font("Helvetica", size=10)
        _line(pdf, 6, "No records available.")
        return bytes(pdf.output())

    for row_number, (_, row) in enumerate(frame.iterrows(), start=1):
        pdf.set_font("Helvetica", "B", 10)
        _line(pdf, 6, f"Record {row_number}")
        pdf.set_font("Helvetica", size=8)
        for column, value in row.items():
            display_value = "NULL" if pd.isna(value) else value
            _line(pdf, 5, f"{column}: {display_value}")
        pdf.ln(2)
    return bytes(pdf.output())
