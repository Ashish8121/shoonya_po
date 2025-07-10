import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO

st.title("Purchase Order Generator (ReportLab)")

# ➡️ Vendor input fields
st.header("Vendor Address")
vendor_name = st.text_input("Vendor Name")
vendor_line1 = st.text_input("Vendor Address Line 1")
vendor_line2 = st.text_input("Vendor Address Line 2")
vendor_gstin = st.text_input("Vendor GSTIN")
vendor_contact = st.text_input("Vendor Contact")
po_id = st.text_input("PO ID")

# ➡️ Initialize session_state for items
if "items" not in st.session_state:
    st.session_state["items"] = []

# ➕ Add new item row button
if st.button("Add New Item Row"):
    st.session_state["items"].append({
        "item_name": "",
        "description": "",
        "hsn_sac": "",
        "qty": 1,
        "amount": 0.0
    })

# ➡️ Render each item row
for idx, item in enumerate(st.session_state["items"]):
    cols = st.columns([1, 3, 5, 2, 1, 2])
    with cols[0]:
        st.markdown(f"{idx+1}")  # S.No
    with cols[1]:
        item_name = st.text_input(f"Item Name {idx+1}", value=item["item_name"], key=f"item_name_{idx}")
    with cols[2]:
        description = st.text_input(f"Description {idx+1}", value=item["description"], key=f"description_{idx}")
    with cols[3]:
        hsn_sac = st.text_input(f"HSN/SAC {idx+1}", value=item["hsn_sac"], key=f"hsn_{idx}")
    with cols[4]:
        qty = st.number_input(f"Qty {idx+1}", min_value=1, value=item["qty"], step=1, key=f"qty_{idx}")
    with cols[5]:
        amount = st.number_input(f"Amount {idx+1}", min_value=0.0, value=item["amount"], step=100.0, key=f"amount_{idx}")

    st.session_state["items"][idx] = {
        "item_name": item_name,
        "description": description,
        "hsn_sac": hsn_sac,
        "qty": qty,
        "amount": amount
    }

# ➡️ Generate PDF button
if st.button("Generate Purchase Order PDF"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()

    # ➡️ Add custom styles
    styles.add(ParagraphStyle(name='POTitleRight', parent=styles['Title'], alignment=TA_RIGHT, fontSize=16))
    styles.add(ParagraphStyle(name='PORight', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=12))

    # ✅ Logo + PURCHASE ORDER right + PO ID below right
    logo_path = "images.png"  # Ensure this path is correct in your project
    im = Image(logo_path, width=50*mm, height=20*mm)

    title_data = [
        [im, Paragraph("<b>PURCHASE ORDER</b>", styles["POTitleRight"])],
        ["", Paragraph(f"PO ID: {po_id}", styles["PORight"])]
    ]

    title_table = Table(title_data, colWidths=[100*mm, 90*mm])
    title_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('ALIGN', (1,1), (1,1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))

    elements.append(title_table)
    elements.append(Spacer(1, 12))

    # ✅ Finvasia and Vendor Address side by side
    finvasia_address = """<b>Finvasia Securities Private Limited</b><br/>
Plot no. D-179, Phase -8 B, Focal point, Mohali SAS Nagar<br/>
Mohali SAS Nagar Punjab 160055<br/>
India<br/>
GSTIN 03AABCF6759K1ZF<br/>
01726750000<br/>
gurpreet.singh@shoonya.com<br/>
"""

    vendor_address = f"""<b>Vendor:</b><br/>
{vendor_name}<br/>
{vendor_line1}<br/>
{vendor_line2}<br/>
GSTIN {vendor_gstin}<br/>
Contact: {vendor_contact}
"""

    address_data = [
        [
            Paragraph(finvasia_address, styles["Normal"]),
            Paragraph(vendor_address, styles["Normal"])
        ]
    ]

    address_table = Table(address_data, colWidths=[95*mm, 95*mm])
    address_table.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))

    elements.append(address_table)
    elements.append(Spacer(1, 12))

    # ➡️ Table data preparation
    table_style = ParagraphStyle(name='TableCell', fontSize=11, leading=16)
    table_style_center = ParagraphStyle(name='TableCellCenter', fontSize=12, leading=16, alignment=TA_CENTER)

    data = [
        [
            Paragraph("S.No", table_style_center),
            Paragraph("Item", table_style_center),
            Paragraph("Description", table_style_center),
            Paragraph("HSN/SAC", table_style_center),
            Paragraph("Qty", table_style_center),
            Paragraph("Amount", table_style_center),
            Paragraph("Amount with GST", table_style_center)
        ]
    ]

    subtotal = 0
    total_igst = 0
    grand_total = 0

    for idx, item in enumerate(st.session_state["items"]):
        unit_price = item["amount"]
        qty = item["qty"]
        amount = unit_price * qty
        igst = amount * 0.18
        amount_with_gst = amount + igst

        row = [
            Paragraph(str(idx + 1), table_style_center),
            Paragraph(item["item_name"], table_style),
            Paragraph(item["description"], table_style),
            Paragraph(item["hsn_sac"], table_style_center),
            Paragraph(str(item["qty"]), table_style_center),
            Paragraph(f"{amount:.2f}", table_style_center),
            Paragraph(f"{amount_with_gst:.2f}", table_style_center)
        ]

        subtotal += amount
        total_igst += igst
        grand_total += amount_with_gst

        data.append(row)

    # ➡️ Calculation rows with proper spans
    calc_style = ParagraphStyle(name='CalcStyle', fontSize=10, alignment=TA_RIGHT)
    data.append([
        '', '', '', '', '', Paragraph("Sub Total", calc_style), Paragraph(f"{subtotal:.2f}", table_style_center)
    ])
    data.append([
        '', '', '', '', '', Paragraph("IGST 18%", calc_style), Paragraph(f"{total_igst:.2f}", table_style_center)
    ])
    data.append([
        '', '', '', '', '', Paragraph("Total", calc_style), Paragraph(f"{grand_total:.2f}", table_style_center)
    ])

    # ➡️ Table styling and append
    table = Table(data, colWidths=[15*mm, 30*mm, 60*mm, 25*mm, 15*mm, 25*mm, 30*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    elements.append(table)



    # ➡️ Build and output
    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()

    st.download_button(
        label="Download Purchase Order PDF",
        data=pdf_value,
        file_name="purchase_order_reportlab.pdf",
        mime="application/pdf"
    )
