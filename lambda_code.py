import json
import boto3
import os
import urllib.parse

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Get bucket and key from the S3 event
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = urllib.parse.unquote_plus(
            event['Records'][0]['s3']['object']['key'], encoding='utf-8'
        )

        # Define destination — same bucket, different prefix (or use a different bucket)
        destination_bucket = os.environ.get('DEST_BUCKET', source_bucket)
        destination_key = f"backup/{source_key}"

        # Copy the object
        copy_source = {'Bucket': source_bucket, 'Key': source_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=destination_bucket,
            Key=destination_key
        )

        print(f"Copied {source_bucket}/{source_key} -> {destination_bucket}/{destination_key}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File copied successfully',
                'source': f"{source_bucket}/{source_key}",
                'destination': f"{destination_bucket}/{destination_key}"
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }