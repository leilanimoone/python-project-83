from validators import url
from urllib.parse import urlparse

def validate_url(url):
    error = ''
    if len(url) == 0:
        error = 'none'
    elif len(url) > 255:
        error = 'max'
    elif not url(url):
        error = 'invalid'
    else:
        parsed_url = urlparse(url)
        normal_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
        url = normal_url
    valid = {'url': url, 'error': error}
    return valid
