import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from base64 import b64encode
from urllib.parse import unquote

def generate_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(100, 750, "Electricity Bill Report")
    pdf.drawString(100, 730, f"Name: {data['name']}")
    pdf.drawString(100, 710, f"Address: {data['address']}")
    pdf.drawString(100, 690, f"Billing Month: {data['billing_month']}")
    pdf.drawString(100, 670, f"Total Consumption: {data['total_consumption']} kWh")
    pdf.drawString(100, 650, f"Total Amount: ${data['total_amount']}")
    pdf.save()
    buffer.seek(0)
    return buffer

def lambda_handler(event, context):
    try:
        # Parse the JSON request
        body = json.loads(event['body'])
        
        # Generate the PDF
        pdf_buffer = generate_pdf(body)
        
        # Encode the PDF file as base64
        pdf_base64 = b64encode(pdf_buffer.read()).decode('utf-8')
        
        # Create the response object
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment; filename=\"electricity_bill.pdf\""
            },
            "body": pdf_base64,
            "isBase64Encoded": True
        }
        
        return response
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "An error occurred",
                "error": str(e)
            })
        }
