import json
import boto3
import base64
import logging

s3_client = boto3.client('s3')
BUCKET_NAME = 'pdf-bill-store2'  # replace with your S3 bucket name

def lambda_handler(event, context):
    try:
        if 'pathParameters' not in event:
            return {
                "statusCode": 400,
                "pathParameters": json.dumps({
                    "message": "'pathParameters' field is missing in the event"
                })
            }
        
        
        
        user_id = event['pathParameters']['user_id']
        billing_month = event['pathParameters']['billing_month']
        
        # Construct the PDF filename
        filename = f"{billing_month}.pdf"

        # Construct the S3 key
        pdf_key = f"electricity_bills/{user_id}/{filename}"
        
        # Get the PDF file from S3
        pdf_object = s3_client.get_object(Bucket=BUCKET_NAME, Key=pdf_key)
        pdf_content = pdf_object['Body'].read()
        
        # Encode the PDF file as base64
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        # Create the response object
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/pdf",
                "Content-Disposition": f"attachment; filename=\"{filename}\""
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