import boto3
import urllib.parse
import json
import os
client = boto3.client('lambda')

def on_file_update(dist, key):
    try:
        if not dist:
            print('Bucket without distribution')
            return {
                "body": 'Bucket without distribution',
                "statusCode": 404
            }
        request = {
            "distribution": dist,
            "path": '/'+key
        }
        print(request)
        client.invoke(
            FunctionName=os.environ['LAMBDA_INVALIDATE'],
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=bytes(json.dumps(request), encoding='utf-8')
        )
    except Exception as e:
        print("exception")
        print(e)
        return {
            "body": str(e),
            "statusCode": 500
        }

    body = {
        "message": "ok"
    }
    print("ok")
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

def on_image_update(event, context):
    if not event:
        event = {"Records": [{"s3": {"bucket": {"name": "north-pole-images"}, "object": {"key": "6/default.png"}}}]}
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print(bucket)
    print(key)
    dist = os.environ['IMAGES_DISTRIBUTION']
    return on_file_update(dist,key)


def on_thumbnail_update(event, context):
    if not event:
        event = {"Records": [{"s3": {"bucket": {"name": "north-pole-thumbnails"}, "object": {"key": "6/default.png"}}}]}
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print(bucket)
    print(key)
    dist = os.environ['THUMBNAILS_DISTRIBUTION']
    return on_file_update(dist,key)


def on_store_image_update(event, context):
    if not event:
        event = {"Records": [{"s3": {"bucket": {"name": "north-pole-stores"}, "object": {"key": "6/default.png"}}}]}
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print(bucket)
    print(key)
    dist = os.environ['STORE_IMAGES_DISTRIBUTION']
    return on_file_update(dist,key)



if __name__ == "__main__":
    on_image_update('', '')