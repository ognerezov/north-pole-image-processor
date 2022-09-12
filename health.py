from urllib.request import urlopen
import json
import boto3
import os

client = boto3.client('lambda')
url = os.environ['HEALTH_CHECK_URL']


def check(event, context):
    try:
        with urlopen(url) as response:
            body = response.read()
            print(body)
            response = {
                "statusCode": 200,
                "body": "ok"
            }

            return response
    except Exception as e:
        print("exception")
        print(e)
        report = {
            "from": "ognerezov@gmail.com",
            "subject": "Warning! Server healthcheck failed",
            "body": str(e)
        }
        client.invoke(
            FunctionName='emailMe',
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=bytes(json.dumps(report), encoding='utf-8')
        )
        return {
            "body": str(e),
            "statusCode": 200
        }


if __name__ == "__main__":
    print(check(event={}, context=''))