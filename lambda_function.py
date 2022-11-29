import boto3
from decimal import Decimal
import json
import urllib.request
import urllib.parse
import urllib.error

#from subprocess import call

print('Loading function')

#call('rm -rf /tmp/*', shell=True)

client_ec2 = boto3.client("ec2")
rekognition = boto3.client('rekognition')
client = boto3.client('sns')
s3 = boto3.client('s3')

# --------------- Helper Functions to call Rekognition APIs ------------------

def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket":'terraform-suresh-s3-bucket', "Name":'888888'}})

    return response


# --------------- Main handler ------------------
def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    # Get the object from the event
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    try:

        # Calls rekognition DetectLabels API to detect labels in S3 object
        response = detect_labels(bucket, key)

        tosend = ""
    
        for Lable in response["Labels"]:
            
            print('{0} - {1}%'.format(Lable["Name"], Lable["Confidence"]))
            tosend += '{0} - {1}%  '.format(Lable["Name"], Lable["Confidence"])
            
        
        with open("/tmp/logs.txt", "w") as f:
            json.dump(tosend, f, indent=2)
            
        s3.upload_file("/tmp/logs.txt", "terraform-suresh-s3-bucket-logs", "logs.txt")
        

        # Print response to console.
        print(response)
        
        message = client.publish(TargetArn='arn:aws:sns:us-east-2:965946476478:cc_proj_sns', Message=tosend, Subject='Image lables')
        
        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e

