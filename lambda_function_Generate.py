import json
import boto3
import uuid
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from base64 import b64encode

s3_client = boto3.client('s3')
BUCKET_NAME = 'pdf-bill-store2'  # replace with your S3 bucket name

RATE_PER_UNIT = 0.35 #Define your rate per unit of consumption


def generate_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(100, 750, "Electricity Bill Report")
    pdf.drawString(100, 730, f"id: {data['id']}")
    pdf.drawString(100, 710, f"Name: {data['name']}")
    pdf.drawString(100, 690, f"Address: {data['address']}")
    pdf.drawString(100, 670, f"Billing Month: {data['billing_month']}")
    pdf.drawString(100, 650, f"Total Consumption: {data['total_consumption']} kWh")
    total_amount = float(data['total_consumption']) * RATE_PER_UNIT
    pdf.drawString(100, 630, f"Total Amount: ${total_amount:.2f}")
    pdf.save()
    buffer.seek(0)
    return buffer

def lambda_handler(event, context):
    try:
        # Check if 'body' is present in the event
        if 'body' not in event:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "'body' field is missing in the event"
                })
            }

        # Parse the JSON request
        body = json.loads(event['body'])
        
        # Generate the PDF
        pdf_buffer = generate_pdf(body)
        
        # Upload PDF to S3
        pdf_key = f"electricity_bills/{body['id']}/{body['billing_month'].replace(' ', '_')}.pdf"
        s3_client.upload_fileobj(pdf_buffer, BUCKET_NAME, pdf_key)
        
        # Generate S3 URL
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{pdf_key}"
        
        # Construct the API Gateway URL
        api_gateway_url = f"https://{event['requestContext']['domainName']}/retrieve-bill/{body['id']}/{body['billing_month'].replace(' ', '_')}"
        
        # Create the response object
        response = {
          "statusCode": 200,
            "body": json.dumps({
                "message": "PDF generated and uploaded to S3 successfully",
                "url": api_gateway_url
                
            })
        
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