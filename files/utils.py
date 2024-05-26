import requests
from django.conf import settings


def generate_simple_url(s3_key):
    s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    simple_url = requests.get(f"https://ks0bm06q4a.execute-api.us-west-2.amazonaws.com/dev?long_url={s3_url}").json()
    return "https://simple-url.skdev.one/"+simple_url['short_url']