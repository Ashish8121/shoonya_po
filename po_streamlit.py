import streamlit as st
from fpdf import FPDF

st.title("Purchase Order Generator")

# 🗂️ Vendor and Deliver To columns
col1, col2 = st.columns(2)

with col1:
    st.header("Vendor Address ")
    vendor_name = st.text_input("Vendor Name")
    vendor_line1 = st.text_input("Vendor Address Line 1")
    vendor_line2 = st.text_input("Vendor Address Line 2")
    vendor_gstin = st.text_input("Vendor GSTIN")
    vendor_contact = st.text_input("Vendor Contact")
    po_id = st.text_input("PO_id")

with col2:
    st.header("Deliver To Address ")
    deliver_name = st.text_input("Deliver To Name")
    deliver_line1 = st.text_input("Deliver To Address Line 1")
    deliver_line2 = st.text_input("Deliver To Address Line 2")
    deliver_gstin = st.text_input("Deliver To GSTIN")
    deliver_contact = st.text_input("Deliver To Contact")

# ➡️ Initialize session_state for dynamic items
if "items" not in st.session_state or not isinstance(st.session_state.get("items"), list):
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

# Render inputs as table-like layout with headers


# Render each item row
for idx, item in enumerate(st.session_state["items"]):
    cols = st.columns([1, 3, 5, 2, 1, 2])

    with cols[0]:
        st.markdown(f"{idx+1}")  # S.No display

    with cols[1]:
        item_name = st.text_input(f"Item Name {idx+1}", value=item.get("item_name", ""), key=f"item_name_{idx}")

    with cols[2]:
        description = st.text_input(f"Description {idx+1}", value=item.get("description", ""), key=f"description_{idx}")

    with cols[3]:
        hsn_sac = st.text_input(f"HSN/SAC {idx+1}", value=item.get("hsn_sac", ""), key=f"hsn_{idx}")

    with cols[4]:
        qty = st.number_input(f"Qty {idx+1}", min_value=1, value=item.get("qty", 1), step=1, key=f"qty_{idx}")

    with cols[5]:
        amount = st.number_input(f"Amount {idx+1}", min_value=0.0, value=item.get("amount", 0.0), step=100.0, key=f"amount_{idx}")

    # Update item in session_state
    st.session_state["items"][idx] = {
        "item_name": item_name,
        "description": description,
        "hsn_sac": hsn_sac,
        "qty": qty,
        "amount": amount
    }

# ➡️ Generate PDF button
if st.button("Generate Purchase Order PDF"):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=25)

    # PURCHASE ORDER
    pdf.text(x=120, y=15, txt="PURCHASE ORDER")
    pdf.set_font("Helvetica", size=10)
    pdf.text(x=120, y=22, txt=f"# PO id: {po_id}")

    # Logo image
    pdf.image("images.png", x=8, y=8, w=60)

    # Finvasia address
    pdf.set_font("Helvetica", "B", size=10)
    pdf.text(x=8, y=30, txt="Finvasia Securities Private Limited")
    pdf.set_font("Helvetica", size=10)
    pdf.set_xy(7, 31)
    finvasia_address = """Plot no. D-179, Phase -8 B, Focal point, Mohali SAS Nagar
Mohali SAS Nagar Punjab 160055
India
GSTIN 03AABCF6759K1ZF
01726750000
gurpreet.singh@shoonya.com
"""
    pdf.multi_cell(w=100, h=5, txt=finvasia_address)
    finvasia_end_y = pdf.get_y()

    # Deliver To block
    pdf.set_font("Helvetica", "B", size=10)
    deliver_start_y = finvasia_end_y + 5
    pdf.text(x=8, y=deliver_start_y, txt="Deliver to : ")
    pdf.set_font("Helvetica", size=10)
    pdf.set_xy(7, deliver_start_y + 2)
    deliver_address = f"""{deliver_name}
{deliver_line1}
{deliver_line2}
GSTIN {deliver_gstin}
Contact: {deliver_contact}"""
    pdf.multi_cell(w=100, h=5, txt=deliver_address)
    deliver_end_y = pdf.get_y()

    # Vendor block
    pdf.set_font("Helvetica", "B", size=10)
    vendor_start_y = 30
    pdf.text(x=120, y=vendor_start_y, txt="Vendor : ")
    pdf.set_font("Helvetica", size=10)
    pdf.set_xy(119, vendor_start_y + 1)
    vendor_address = f"""{vendor_name}
{vendor_line1}
{vendor_line2}
GSTIN {vendor_gstin}
Contact: {vendor_contact}"""
    pdf.multi_cell(w=80, h=5, txt=vendor_address)

    # ➡️ Table header
    headers = ["S.No", "Item", "Description", "HSN/SAC", "Qty", "Amount"]
    start_x = 5
    start_y = max(deliver_end_y, pdf.get_y()) + 10
    col_widths = [15, 20, 100, 25, 10, 30]

    pdf.set_fill_color(200, 200, 200)
    pdf.set_xy(start_x, start_y)
    for header, width in zip(headers, col_widths):
        pdf.cell(width, 10, header, border=1, align='C', fill=True)
    pdf.ln()

    # ➡️ Table rows with wrapping
    total_amount = 0
    line_height = 7  # Increased for better vertical spacing
    pdf.set_y(start_y + 10)

    for idx, item in enumerate(st.session_state["items"]):
        row = [
            str(idx + 1),
            item["item_name"],
            item["description"],
            item["hsn_sac"],
            str(item["qty"]),
            str(item["amount"])
        ]

        # Get wrapped lines for each cell to find max lines for the row
        cell_lines = []
        max_lines = 1
        for val, width in zip(row, col_widths):
            lines = pdf.multi_cell(width, line_height, val, border=0, align='C', split_only=True)
            cell_lines.append(lines)
            max_lines = max(max_lines, len(lines))

        row_height = max_lines * line_height

        # Check if page break needed
        if pdf.get_y() + row_height > 270:
            pdf.add_page()
            pdf.set_fill_color(200, 200, 200)
            pdf.set_xy(start_x, pdf.get_y())
            for header, width in zip(headers, col_widths):
                pdf.cell(width, 10, header, border=1, align='C', fill=True)
            pdf.ln()

        y_before = pdf.get_y()
        x_before = start_x

        # Draw each line of the row
        for line_idx in range(max_lines):
            x = x_before
            for col_idx, lines in enumerate(cell_lines):
                text = lines[line_idx] if line_idx < len(lines) else ""
                pdf.set_xy(x, y_before + line_idx * line_height)
                pdf.cell(col_widths[col_idx], line_height, text, border=1, align='C')
                x += col_widths[col_idx]

        # Move cursor below this row
        pdf.set_y(y_before + row_height)
        total_amount += float(item["amount"])

    # ➡️ IGST and Total calculation
    igst = total_amount * 0.18
    grand_total = total_amount + igst

    pdf.set_x(start_x + sum(col_widths[:-2]))
    pdf.cell(col_widths[-2], 10, "Sub Total:", border=0, align='R')
    pdf.cell(col_widths[-1], 10, f"{total_amount:.2f}", border=1, align='C')
    pdf.ln()

    pdf.set_x(start_x + sum(col_widths[:-2]))
    pdf.cell(col_widths[-2], 10, "IGST 18%:", border=0, align='R')
    pdf.cell(col_widths[-1], 10, f"{igst:.2f}", border=1, align='C')
    pdf.ln()

    pdf.set_x(start_x + sum(col_widths[:-2]))
    pdf.set_font("Helvetica", "B", size=10)
    pdf.cell(col_widths[-2], 10, "Total:", border=0, align='R')
    pdf.set_font("Helvetica", size=10)
    pdf.cell(col_widths[-1], 10, f"{grand_total:.2f}", border=1, align='C')
    pdf.ln(20)

    # ➡️ Authorized Signature
    if pdf.get_y() + 20 > 270:
        pdf.add_page()
    pdf.set_font("Helvetica", "B", size=12)
    pdf.cell(0, 10, "Authorized Signature", ln=True, align='L')

    # Save PDF and provide download button
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin1')


    st.download_button(
        label="Download Purchase Order PDF",
        data=pdf_bytes,
        file_name="purchase_order.pdf",
        mime="application/pdf"
    )
