import boto3
import json

def lambda_handler(event, context):
    # Parsed from s3://testing-s3-abcdefg/backup/example_currencies.csv
    bucket_name = "testing-s3-abcdefg"
    object_key = "backup/example_currencies.csv"
    
    s3_client = boto3.client('s3', region_name='us-east-1') # Ensure region matches bucket

    try:
        # Generating URL for downloading the file (get_object)
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key
            },
            ExpiresIn=3600
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'download_url': response})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }