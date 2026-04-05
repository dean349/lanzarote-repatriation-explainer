
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

output_path = os.path.join(
    os.path.dirname(__file__),
    "Calpe Notary Invoice - Beneficial Owner Declaration Act 10-2010 (A4 01025).pdf"
)

doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm,
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    "Title", parent=styles["Heading1"],
    fontSize=16, textColor=colors.HexColor("#1a3c5e"),
    alignment=TA_CENTER, spaceAfter=4
)
subtitle_style = ParagraphStyle(
    "Subtitle", parent=styles["Normal"],
    fontSize=10, textColor=colors.HexColor("#5a5a5a"),
    alignment=TA_CENTER, spaceAfter=2
)
section_style = ParagraphStyle(
    "Section", parent=styles["Heading2"],
    fontSize=11, textColor=colors.HexColor("#1a3c5e"),
    spaceBefore=12, spaceAfter=4
)
body_style = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=9, leading=13, textColor=colors.HexColor("#333333")
)
small_style = ParagraphStyle(
    "Small", parent=styles["Normal"],
    fontSize=7.5, leading=11, textColor=colors.HexColor("#555555")
)

# Colour palette
DARK_BLUE  = colors.HexColor("#1a3c5e")
LIGHT_BLUE = colors.HexColor("#e8f1f8")
MID_BLUE   = colors.HexColor("#3a7cbf")
GREY       = colors.HexColor("#f5f5f5")

elements = []

# ── HEADER ───────────────────────────────────────────────────────────────────
elements.append(Paragraph("NOTARIAL INVOICE", title_style))
elements.append(Paragraph(
    "Beneficial Owner Declaration — Act 10/2010 — No Monetary Value",
    subtitle_style
))
elements.append(Paragraph(
    "Invoice No: <b>A4 / 01025</b>   |   Date: <b>20 March 2026</b>",
    subtitle_style
))
elements.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE, spaceAfter=10))

# ── PARTIES ──────────────────────────────────────────────────────────────────
elements.append(Paragraph("PARTIES", section_style))
party_data = [
    [Paragraph("<b>BILLED TO</b>", body_style), Paragraph("<b>ISSUED BY</b>", body_style)],
    [
        Paragraph(
            "<b>LOS ROMEROS LIMITED</b><br/>"
            "1-2 Albert Chambers, Canal Street, No. 1-2<br/>"
            "CW12 4AA, Congleton<br/>"
            "<b>UNITED KINGDOM</b>",
            body_style
        ),
        Paragraph(
            "<b>JOSÉ MIGUEL DE LAMO IGLESIAS</b><br/>"
            "Tax ID (NIF): 12730806F<br/>"
            "Plaza Del Moscatell, s/n – Edif. Cristina, ground floor<br/>"
            "03710 – Calpe (Alicante), Spain<br/>"
            "Tel: 965 830 816 | Fax: 965 836 301<br/>"
            "Email: migueldelamo@notariado.org",
            body_style
        ),
    ],
]
party_table = Table(party_data, colWidths=[8.5*cm, 8.5*cm])
party_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
    ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
    ("FONTSIZE",   (0, 0), (-1, 0), 9),
    ("BACKGROUND", (0, 1), (0, 1), LIGHT_BLUE),
    ("BACKGROUND", (1, 1), (1, 1), GREY),
    ("VALIGN",     (0, 0), (-1, -1), "TOP"),
    ("PADDING",    (0, 0), (-1, -1), 8),
    ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("LINEBELOW",  (0, 0), (-1, 0), 1, DARK_BLUE),
]))
elements.append(party_table)
elements.append(Spacer(1, 6))

# ── TRANSACTION DETAILS ───────────────────────────────────────────────────────
elements.append(Paragraph("TRANSACTION DETAILS", section_style))
trans_data = [
    ["Protocol Number",        "N8261069B / 1087"],
    ["Legal Transaction",      "Beneficial Owner Declaration — Act 10/2010 (NO MONETARY VALUE)"],
    ["Tariff Reduction Applied", "21%"],
]
trans_table = Table(trans_data, colWidths=[5*cm, 12*cm])
trans_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
    ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE",   (0, 0), (-1, -1), 9),
    ("PADDING",    (0, 0), (-1, -1), 6),
    ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, GREY]),
]))
elements.append(trans_table)
elements.append(Spacer(1, 6))

# ── FEE BREAKDOWN ─────────────────────────────────────────────────────────────
elements.append(Paragraph("FEE BREAKDOWN", section_style))
fee_headers = [
    Paragraph("<b>Description</b>", body_style),
    Paragraph("<b>Units</b>", body_style),
    Paragraph("<b>Tariff</b>", body_style),
    Paragraph("<b>VAT</b>", body_style),
    Paragraph("<b>Amount</b>", body_style),
]
fee_rows = [
    ["Beneficial Owner Declaration — Act 10/2010", "1", "2",  "21%", "€36.06"],
    ["Authorised Electronic Copy",                  "1", "2",  "21%", "€66.11"],
    ["Excess pages – Original Deed",               "14", "7",  "21%", "€42.07"],
    ["Excess pages – Electronic Original",         "14", "7",  "21%", "€42.07"],
    ["Protocol Electronic Incorporation Note",      "1", "6",  "21%", "€3.01"],
    ["Protocol Electronic Deposit Note",            "1", "6",  "21%", "€3.01"],
    ["Certified Copy – 5-page Exhibition",          "1", "5",  "21%", "€5.41"],
    [Paragraph("<b>TOTAL FEES</b>", body_style),   "", "", "",  Paragraph("<b>€197.74</b>", body_style)],
]
fee_data = [fee_headers] + fee_rows
fee_table = Table(fee_data, colWidths=[7.5*cm, 1.5*cm, 1.5*cm, 1.5*cm, 2.5*cm])
fee_table.setStyle(TableStyle([
    ("BACKGROUND",     (0, 0), (-1, 0), DARK_BLUE),
    ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
    ("FONTSIZE",       (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, GREY]),
    ("BACKGROUND",     (0, -1), (-1, -1), LIGHT_BLUE),
    ("FONTNAME",       (0, -1), (-1, -1), "Helvetica-Bold"),
    ("ALIGN",          (1, 0), (-1, -1), "CENTER"),
    ("ALIGN",          (-1, 1), (-1, -1), "RIGHT"),
    ("PADDING",        (0, 0), (-1, -1), 6),
    ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("LINEBELOW",      (0, 0), (-1, 0), 1, DARK_BLUE),
    ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
]))
elements.append(fee_table)
elements.append(Spacer(1, 6))

# ── DISBURSEMENTS ─────────────────────────────────────────────────────────────
elements.append(Paragraph("DISBURSEMENTS", section_style))
disb_data = [
    [Paragraph("<b>Description</b>", body_style), Paragraph("<b>Units</b>", body_style),
     Paragraph("<b>VAT</b>", body_style), Paragraph("<b>Amount</b>", body_style)],
    ["Stamped Paper – Original Deed (Rule 8)", "12", "Not subject", "€1.80"],
    [Paragraph("<b>TOTAL DISBURSEMENTS</b>", body_style), "", "",
     Paragraph("<b>€1.80</b>", body_style)],
]
disb_table = Table(disb_data, colWidths=[9*cm, 1.5*cm, 2.5*cm, 2.5*cm])
disb_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), MID_BLUE),
    ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
    ("FONTSIZE",   (0, 0), (-1, -1), 9),
    ("BACKGROUND", (0, 1), (-1, 1), GREY),
    ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BLUE),
    ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
    ("ALIGN",      (1, 0), (-1, -1), "CENTER"),
    ("ALIGN",      (-1, 1), (-1, -1), "RIGHT"),
    ("PADDING",    (0, 0), (-1, -1), 6),
    ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
]))
elements.append(disb_table)
elements.append(Spacer(1, 6))

# ── INVOICE SUMMARY ───────────────────────────────────────────────────────────
elements.append(Paragraph("INVOICE SUMMARY", section_style))
summary_data = [
    ["Taxable Base (subject to VAT):", "€197.74"],
    ["Non-taxable Base:",              "€1.80"],
    ["VAT (21% on €197.74):",         "€41.53"],
    [Paragraph("<b>TOTAL INVOICE</b>", body_style),
     Paragraph("<b>€241.07</b>", body_style)],
]
summary_table = Table(summary_data, colWidths=[11*cm, 4*cm])
summary_table.setStyle(TableStyle([
    ("ALIGN",          (1, 0), (1, -1), "RIGHT"),
    ("FONTSIZE",       (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 0), (-1, -2), [colors.white, GREY]),
    ("BACKGROUND",     (0, -1), (-1, -1), DARK_BLUE),
    ("TEXTCOLOR",      (0, -1), (-1, -1), colors.white),
    ("FONTNAME",       (0, -1), (-1, -1), "Helvetica-Bold"),
    ("FONTSIZE",       (0, -1), (-1, -1), 11),
    ("PADDING",        (0, 0), (-1, -1), 7),
    ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("LINEABOVE",      (0, -1), (-1, -1), 2, DARK_BLUE),
    ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
]))
elements.append(summary_table)
elements.append(Spacer(1, 6))

# ── PAYMENT INSTRUCTIONS ──────────────────────────────────────────────────────
elements.append(Paragraph("PAYMENT INSTRUCTIONS", section_style))
pay_data = [
    ["Payment Method:", "Bank Transfer"],
    ["Due Date:",       "20 March 2026"],
    ["IBAN:",           "ES37 0182 0130 47 0201639164"],
    ["Payment Reference:", "A4 / 01025  (please include when making payment)"],
]
pay_table = Table(pay_data, colWidths=[4*cm, 13*cm])
pay_table.setStyle(TableStyle([
    ("BACKGROUND",     (0, 0), (0, -1), LIGHT_BLUE),
    ("FONTNAME",       (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE",       (0, 0), (-1, -1), 9),
    ("PADDING",        (0, 0), (-1, -1), 6),
    ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, GREY]),
]))
elements.append(pay_table)
elements.append(Spacer(1, 10))

# ── LEGAL NOTICES ──────────────────────────────────────────────────────────────
elements.append(HRFlowable(width="100%", thickness=1, color=MID_BLUE, spaceAfter=6))
elements.append(Paragraph("LEGAL NOTICES", section_style))
elements.append(Paragraph(
    "<b>Invoice Disputes:</b> Interested parties may contest this invoice within <b>15 working days</b> "
    "of receipt — either before the authorising Notary or directly to the Board of the Notarial College "
    "of Valencia, under <b>Royal Decree 1426/1989</b> (BOE 28 November 1989), Annex II, General Rule 10.",
    small_style
))
elements.append(Spacer(1, 4))
elements.append(Paragraph(
    "<b>Data Protection:</b> Personal data is processed strictly confidentially in accordance with "
    "<b>Organic Law 15/1999 of 13 December</b> (Data Protection Act). Data may be shared with public "
    "authorities to fulfil legal obligations. Rights of access, rectification, cancellation and "
    "objection may be exercised by post to the Notary's office.",
    small_style
))
elements.append(Spacer(1, 8))
elements.append(HRFlowable(width="100%", thickness=1, color=MID_BLUE, spaceAfter=4))
elements.append(Paragraph(
    "<i>Translated from Spanish original. Issued by Notary José Miguel de Lamo Iglesias, Calpe (Alicante), Spain.</i>",
    ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontSize=7, textColor=colors.HexColor("#888888"),
        alignment=TA_CENTER
    )
))

# ── BUILD ──────────────────────────────────────────────────────────────────────
doc.build(elements)
print(f"PDF created successfully:\n{output_path}")
