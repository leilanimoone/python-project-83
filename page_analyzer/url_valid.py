from validators import url


def validate_url(url):
    error = []
    if url == '':
        error.extend(['Некорректный URL', 'URL обязателен'])
    elif not url(url):
        error.append('Некорректный URL')
    return error

