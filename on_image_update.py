import json
import os
import boto3
from PIL import Image, ImageDraw
import urllib.parse
from io import BytesIO


s3 = boto3.client('s3')


def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def crop_to_square(im):
    (left, top, right, bottom) = im.getbbox()
    if right > bottom:
        delta = (right - bottom) / 2
        left += delta
        right -= delta
    else:
        delta = (bottom - right) / 2
        top += delta
        bottom -= delta

    return im.crop((left, top, right, bottom))


def resize(im, sz):
    size = sz, sz
    image_copy = im.copy()
    image_copy.thumbnail(size, Image.ANTIALIAS)
    return image_copy


def get_s3_filestream(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    return response['Body']


def upload_image(im, bucket, key, fmt):
    print(f'called upload with bucket {bucket} and key {key} format: {fmt}')
    if fmt == "JPEG":
        print("converting")
        im = im.convert('RGB')
    print(im.mode)
    file_stream = BytesIO()
    im.save(file_stream, format=fmt)
    result = s3.put_object(Bucket=bucket, Key=key, Body=file_stream.getvalue())
    print(result)


def on_image_update(event, context):
    try:
        if not event:
            event = {"Records": [{"s3": {"bucket": {"name": "north-pole-original-images"}, "object": {"key": "6/default.png"}}}]}
        print(event)
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        print(bucket)
        print(key)
        with Image.open(get_s3_filestream(bucket, key)) as im:
            im1 = crop_to_square(im)

            image = resize(im1, int(os.environ['IMAGE_SIZE']))
            # image.show()
            pre, ext = os.path.splitext(key)

            thumbnail = resize(im1, int(os.environ['ICON_SIZE']))
            thumbnail = add_corners(thumbnail, int(os.environ['CORNER_RADIUS']))
            # thumbnail.show()
            upload_image(thumbnail, os.environ['THUMBNAILS_BUCKET'], pre + '.png', 'png')
            upload_image(image, os.environ['OUTPUT_BUCKET'], pre + '.jpg', 'JPEG')
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
    on_image_update('', '')
