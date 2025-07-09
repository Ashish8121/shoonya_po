import streamlit as st
from fpdf import FPDF
from io import BytesIO
from textwrap import wrap

st.title("Purchase Order Generator")

# 🗂️ Vendor and Deliver To columns


st.header("Vendor Address ")
vendor_name = st.text_input("Vendor Name")
vendor_line1 = st.text_input("Vendor Address Line 1")
vendor_line2 = st.text_input("Vendor Address Line 2")
vendor_gstin = st.text_input("Vendor GSTIN")
vendor_contact = st.text_input("Vendor Contact")
po_id = st.text_input("PO_id")



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
    pdf.set_font("Helvetica", size=20)

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
    start_y = max(finvasia_end_y, pdf.get_y()) + 10
    col_widths = [15, 20, 100, 25, 10, 30]
    line_height = 5

    pdf.set_fill_color(200, 200, 200)
    pdf.set_xy(start_x, start_y)
    for header, width in zip(headers, col_widths):
        pdf.cell(width, 10, header, border=1, align='C', fill=True)
    pdf.ln()

    # ➡️ Table rows with wrapping
    total_amount = 0
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

        x_positions = [start_x + sum(col_widths[:i]) for i in range(len(col_widths))]
        y_start = pdf.get_y()
        max_y = y_start

        for col_idx, val in enumerate(row):
            x = x_positions[col_idx]
            y = pdf.get_y()
            pdf.set_xy(x, y)
            pdf.multi_cell(col_widths[col_idx], line_height, val, border=0, align='C')
            max_y = max(max_y, pdf.get_y())
            pdf.set_xy(x + col_widths[col_idx], y)

        row_height = max_y - y_start

        if pdf.get_y() + row_height > 270:
            pdf.add_page()
            pdf.set_fill_color(200, 200, 200)
            pdf.set_xy(start_x, pdf.get_y())
            for header, width in zip(headers, col_widths):
                pdf.cell(width, 10, header, border=1, align='C', fill=True)
            pdf.ln()
            y_start = pdf.get_y()
            max_y = y_start

        pdf.set_y(y_start)
        for col_idx, val in enumerate(row):
            x = x_positions[col_idx]
            pdf.set_xy(x, y_start)
            pdf.multi_cell(col_widths[col_idx], line_height, val, border=1, align='C')
            pdf.set_xy(x + col_widths[col_idx], y_start)

        pdf.set_y(max_y)
        total_amount += float(item["amount"])

    # ➡️ IGST and Total calculation (moved outside the loop)
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


    # Output PDF as BytesIO
    pdf_output = pdf.output(dest='S').encode('latin1') if isinstance(pdf.output(dest='S'), str) else pdf.output(dest='S')
    pdf_bytes = BytesIO(pdf_output)

    st.download_button(
        label="Download Purchase Order PDF",
        data=pdf_bytes,
        file_name="purchase_order.pdf",
        mime="application/pdf"
    )
