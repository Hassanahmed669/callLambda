import json
import requests
import base64
import boto3
import os

counter = 0

def save_locally(images_binary, local_file_path):
    with open(local_file_path, "wb") as image_file:
        image_file.write(images_binary)

def upload_to_s3(local_file_path, s3_bucket_name, s3_file_name):
    s3 = boto3.client('s3', region_name='ap-south-1')
    try:
        s3.upload_file(local_file_path, s3_bucket_name, s3_file_name)
        return True
    except Exception as e:
        print(f"Failed to upload to S3: {e}")
        return False

def lambda_handler(event, context):
    global counter
    request_body = json.loads(event['body'])
    api_data = {
        "prompt": request_body.get("prompt", ""),
        "steps": 25,
        "cfg_scale": 7,
        "width": 512,
        "height": 512,
    }
    api_url = "http://13.234.66.240:7860/sdapi/v1/txt2img"
    api_response = requests.post(api_url, json=api_data)

    if api_response.status_code == 200:
        api_response_body = api_response.json()
        images_base64 = api_response_body['images'][0]
        images_binary = base64.b64decode(images_base64)
        counter += 1
        file_name = f"output_image-{counter:04d}.png"
        local_file_path = f"/tmp/{file_name}"
        save_locally(images_binary, local_file_path)
        s3_bucket_name = "stable-png-images"
        s3_file_name = file_name
        upload_success = upload_to_s3(local_file_path, s3_bucket_name, s3_file_name)

        if upload_success:
            response = {
                "statusCode": 200,
                "body": json.dumps({
                    "original_request": request_body,
                    "external_api_response": {"images": f"s3://{s3_bucket_name}/{s3_file_name}"}
                })
            }
        else:
            response = {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to upload image to S3"})
            }
    else:
        response = {
            "statusCode": api_response.status_code,
            "body": json.dumps({"error": "External API request failed"})
        }

    return response
