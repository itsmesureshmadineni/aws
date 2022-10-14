import boto3
from decimal import Decimal
import json
import urllib.request
import urllib.parse
import urllib.error

print('Loading function')

rekognition = boto3.client('rekognition')
client = boto3.client('sns')

# --------------- Helper Functions to call Rekognition APIs ------------------

def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})

    
        
    return response


# --------------- Main handler ------------------


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    try:
        # Calls rekognition DetectFaces API to detect faces in S3 object
        #response = detect_faces(bucket, key)

        # Calls rekognition DetectLabels API to detect labels in S3 object
        response = detect_labels(bucket, key)

        tosend = ""
    
        for Lable in response["Labels"]:
            
            print('{0} - {1}%'.format(Lable["Name"], Lable["Confidence"]))
            tosend+= '{0} - {1}%'.format(Lable["Name"], Lable["Confidence"])
        
        # Calls rekognition IndexFaces API to detect faces in S3 object and index faces into specified collection
        #response = index_faces(bucket, key)
 
        # Print response to console.
        print(response)
        
        message = client.publish(TargetArn='arn:aws:sns:us-east-1:965946476478:cc_project_us1', Message=tosend, Subject='Image lables')
        
        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e

