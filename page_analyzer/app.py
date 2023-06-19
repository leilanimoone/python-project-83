import os
import requests
from flask import (Flask,
                   request,
                   url_for,
                   flash,
                   redirect,
                   render_template,
                   get_flashed_messages)
from datetime import datetime
from dotenv import load_dotenv
from page_analyzer.url_valid import validate_url
from page_analyzer.html import get_page_content
from page_analyzer.data import (get_connection,
                                close,
                                get_urls_by_id,
                                get_urls_by_name,
                                get_all_urls,
                                add_site,
                                add_check,
                                get_checks_by_id)


load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    conn = get_connection()
    urls = get_all_urls(conn)
    close(conn)
    messages = get_flashed_messages(with_categories=True)
    return render_template('urls.html', urls=urls, messages=messages)


@app.post('/urls')
def urls_post():
    url = request.form.get('url')
    check = validate_url(url)
    conn = get_connection()
    found = get_urls_by_name(check['url'], conn)
    close(conn)

    if found:
        check['error'] = 'exists'
    url = check['url']
    error = check['error']

    if error == 'exists':
        conn = get_connection()
        url_id_ = get_urls_by_name(url, conn)['id']
        close(conn)
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_show', url_id_=url_id_))
    elif error == 'zero':
        flash('Некорректный URL', 'alert-danger')
        flash('URL обязателен', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, messages=messages), 422
    elif error == 'length':
        flash('Некорректный URL', 'alert-danger')
        flash('URL превышает 255 символов', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, messages=messages), 422
    elif error == 'invalid':
        flash('Некорректный URL', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, messages=messages), 422
    else:
        site = {'url': url,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        conn = get_connection()
        add_site(site, conn)
        close(conn)
        conn = get_connection()
        url_id_ = get_urls_by_name(url, conn)['id']
        close(conn)
        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for('url_show', url_id_=url_id_))


@app.route('/urls/<url_id_>')
def url_show(url_id_):
    try:
        conn = get_connection()
        url = get_urls_by_id(url_id_, conn)
        close(conn)
        conn = get_connection()
        checks = get_checks_by_id(url_id_, conn)
        close(conn)
        messages = get_flashed_messages(with_categories=True)
        file = 'show_url.html'
        return render_template(file, url=url, checks=checks, messages=messages)
    except IndexError:
        return render_template('error.html'), 404


@app.post('/urls/<url_id_>/checks')
def url_check(url_id_):
    conn = get_connection()
    url = get_urls_by_id(url_id_, conn)['name']
    close(conn)
    try:
        check = get_page_content(url)
        check['url_id'] = url_id_
        check['checked_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        add_check(check, conn)
        close(conn)
        flash('Страница успешно проверена', 'alert-success')
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
    return redirect(url_for('url_show', url_id_=url_id_))


if __name__ == '__main__':
    app.run()
