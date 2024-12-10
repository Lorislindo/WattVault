import json
import boto3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import tempfile

s3_client = boto3.client('s3')
BUCKET_NAME = 'your-s3-bucket-name'  # Replace with your S3 bucket name
RATE_PER_UNIT = 0.15  # Define your rate per unit of consumption

def generate_pdf(user_id, billing_month, total_consumption):
    total_amount = total_consumption * RATE_PER_UNIT

    pdf_file_path = os.path.join(tempfile.gettempdir(), f"{billing_month}.pdf")
    c = canvas.Canvas(pdf_file_path, pagesize=letter)
    c.drawString(100, 750, f"User ID: {user_id}")
    c.drawString(100, 730, f"Billing Month: {billing_month}")
    c.drawString(100, 710, f"Total Consumption: {total_consumption} kWh")
    c.drawString(100, 690, f"Total Amount: ${total_amount:.2f}")
    c.save()

    return pdf_file_path

def lambda_handler(event, context):
    try:
        # Extract the data from the JSON body
        body = json.loads(event['body'])
        user_id = body['user_id']
        billing_month = body['billing_month']
        total_consumption = body['total_consumption']
        
        # Generate the PDF
        pdf_file_path = generate_pdf(user_id, billing_month, total_consumption)
        
        # Upload the PDF to S3
        s3_key = f"electricity_bills/{user_id}/{billing_month}.pdf"
        with open(pdf_file_path, 'rb') as pdf_file:
            s3_client.upload_fileobj(pdf_file, BUCKET_NAME, s3_key)

        # Remove the temporary PDF file
        os.remove(pdf_file_path)

        # Construct the API Gateway URL
        api_gateway_url = f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}/retrieve-bill/{user_id}/{billing_month}"
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "PDF generated and uploaded to S3 successfully",
                "url": api_gateway_url
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "An error occurred",
                "error": str(e)
            })
        }
