import boto3
import json
import os

s3 = boto3.client('s3')


def delete_folder(bucket, prefix):
    print(prefix)
    print(bucket)
    result = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    print(result)
    if result.get('KeyCount') > 0:
        for o in result.get('Contents'):
            key = o.get('Key')
            print(key)
            s3.delete_objects(Bucket=bucket, Delete={
                'Objects': [
                    {
                        'Key': key
                    },
                ],
                'Quiet': True
            })

        s3.delete_objects(Bucket=bucket, Delete={
            'Objects': [
                {
                    'Key': prefix + '/'
                },
            ],
            'Quiet': True
        })


def on_item_delete(event, context):
    try:
        if not event:
            event = {"item": '47'}
        prefix = event["item"]
        print(prefix)
        delete_folder(os.environ['ORIGINALS_BUCKET'], prefix)
        delete_folder(os.environ['OUTPUT_BUCKET'], prefix)
        delete_folder(os.environ['THUMBNAILS_BUCKET'], prefix)

    except Exception as e:
        print("exception")
        print(e)
        return {
            "body": str(e),
            "statusCode": 500
        }

    body = {
        "message": "ok",
        "input": event
    }
    print("ok")
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


if __name__ == "__main__":
    on_item_delete({'item': '46'}, '')
