from fpdf import FPDF
import uuid

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=25)

# PURCHASE ORDER at top right
pdf.text(x=120, y=15, txt="PURCHASE ORDER")

# PO ID below PURCHASE ORDER
po_id = 1
pdf.set_font("Helvetica", size=10)
pdf.text(x=120, y=22, txt=f"# PO id: {po_id}")

# Logo image
pdf.image("images.png", x=8, y=8, w=60)

# Bold company name - Finvasia
pdf.set_font("Helvetica", "B", size=10)
pdf.text(x=8, y=30, txt="Finvasia Securities Private Limited")

# Finvasia address block
pdf.set_font("Helvetica", size=10)
pdf.set_xy(7, 33)
finvasia_address = """Plot no. D-179, Phase -8 B, Focal point, Mohali SAS Nagar
Mohali SAS Nagar Punjab 160055
India
GSTIN 03AABCF6759K1ZF
01726750000
gurpreet.singh@shoonya.com
https://finvasia.com/"""
pdf.multi_cell(w=100, h=5, txt=finvasia_address)
finvasia_end_y = pdf.get_y()

# Deliver To block directly under Finvasia
pdf.set_font("Helvetica", "B", size=10)
deliver_start_y = finvasia_end_y + 5
pdf.text(x=8, y=deliver_start_y, txt="Deliver to : ")
pdf.set_font("Helvetica", size=10)
pdf.set_xy(7, deliver_start_y + 2)
deliver_address = """Deliver To Name
Deliver To Address Line 1
Deliver To Address Line 2
GSTIN XXXXXXXXXXX
Contact: 9876543210"""
pdf.multi_cell(w=100, h=5, txt=deliver_address)
deliver_end_y = pdf.get_y()

# Vendor block under PURCHASE ORDER on right
pdf.set_font("Helvetica", "B", size=10)
vendor_start_y = 30  # below PURCHASE ORDER title
pdf.text(x=120, y=vendor_start_y, txt="Vendor : ")
pdf.set_font("Helvetica", size=10)
pdf.set_xy(119, vendor_start_y + 2)
vendor_address = """Vendor Company Name
Vendor Address Line 1
Vendor Address Line 2
GSTIN XXXXXXXXXXX
Contact: 9876543210"""
pdf.multi_cell(w=80, h=5, txt=vendor_address)
vendor_end_y = pdf.get_y()

# Determine starting y for table based on deliver_end_y
table_start_y = deliver_end_y + 10

# Table header data
headers = ["S.No", "Item", "Description", "HSN/SAC", "Qty", "Amount"]
start_x = 5
start_y = table_start_y
col_widths = [15, 20, 100, 25, 10, 30]

# Header row with highlight
pdf.set_fill_color(200, 200, 200)
pdf.set_text_color(0, 0, 0)
pdf.set_xy(start_x, start_y)
for i in range(len(headers)):
    pdf.cell(col_widths[i], 10, headers[i], border=1, align='C', fill=True)
pdf.ln()

# Dummy table data
data = [
    ["1", "Laptop", "Intel i7, 16GB RAM w", "8471", "1", "80000"],
    ["2", "Monitor", "24 inch LED", "8528", "2", "20000"],
    ["3", "Mouse", "Wireless Optical Mouse with ", "8471", "5", "2500"],
] * 10

# Add spacing within cells
line_height = 7

# Draw table rows with wrapping and spacing
total_amount = 0
pdf.set_y(start_y + 10)

for row in data:
    # Calculate max lines needed
    line_heights = []
    for i in range(len(row)):
        lines = pdf.multi_cell(col_widths[i], line_height, row[i], border=0, align='C', split_only=True)
        line_heights.append(len(lines))

    max_lines = max(line_heights)
    row_height = max_lines * line_height

    # Check page break
    if pdf.get_y() + row_height > 270:
        pdf.add_page()
        # Re-draw header
        pdf.set_fill_color(200, 200, 200)
        pdf.set_xy(start_x, pdf.get_y())
        for i in range(len(headers)):
            pdf.cell(col_widths[i], 10, headers[i], border=1, align='C', fill=True)
        pdf.ln()

    y_before = pdf.get_y()
    x_before = start_x

    for i in range(len(row)):
        pdf.set_xy(x_before, y_before)
        pdf.multi_cell(col_widths[i], line_height, row[i], border=1, align='C')
        x_before += col_widths[i]

    pdf.set_y(y_before + row_height)
    total_amount += int(row[-1])

# IGST and Total calculation
igst = total_amount * 0.18
grand_total = total_amount + igst

# Check page break before totals
if pdf.get_y() + 30 > 270:
    pdf.add_page()

# Subtotal, IGST, Total rows
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

# Check page break before authorized signature
if pdf.get_y() + 20 > 270:
    pdf.add_page()

# Authorized signature on the left
pdf.set_font("Helvetica", "B", size=12)
pdf.cell(0, 10, "Authorized Signature", ln=True, align='L')

# Output PDF
pdf.output("po_fpdf_text_method.pdf")
