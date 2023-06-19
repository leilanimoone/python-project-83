import validators
from urllib.parse import urlparse


def validate_url(url):
    error = ''
    if len(url) == 0:
        error = 'zero'
    elif len(url) > 255:
        error = 'length'
    elif not validators.url(url):
        error = 'invalid'
    else:
        parsed_url = urlparse(url)
        normal_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
        url = normal_url
    valid = {'url': url, 'error': error}
    return valid
