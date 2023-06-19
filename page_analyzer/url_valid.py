import validators


def validate_url(url):
    error = []
    if url == '':
        error.extend(['Некорректный URL', 'URL обязателен'])
    elif not validators.url(url):
        error.append('Некорректный URL')
    return error
