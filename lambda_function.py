import json

def lambda_handler(event, context):
    request_body = json.loads(event['body'])

    response = {
        "statusCode": 200,
        "body": json.dumps(request_body)
    }

    return response
