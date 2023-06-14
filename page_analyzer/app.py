from flask import Flask, request, url_for, flash, redirect, render_template, get_flashed_messages
import os
import requests
from datetime import datetime
from psycopg2 import connect
from dotenv import load_dotenv
from page_analyzer.url_valid import validate_url
from page_analyzer.html import get_page_content
from page_analyzer.data import add_check, get_checks_by_id, get_urls_by_name, add_site, get_all_urls, get_urls_by_id

 
app = Flask(__name__)
 
 
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def urls_post():
    url = request.form.get('url')
    check = validate_url(url)
    conn = connect(os.getenv('DATABASE_URL'))
    found = get_urls_by_name(check['url'], conn)
    conn.close()
    if found:
        check['error'] = 'exists'
    url = check['url']
    error = check['error']
    if error == 'exists':
        conn = connect(os.getenv('DATABASE_URL'))
        url_id_ = get_urls_by_name(url, conn)['id']
        conn.close()
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_show', url_id_=url_id_))
    elif error == 'max':
        flash('Некорректный URL', 'alert-danger')
        flash('URL превышает 255 символов', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, messages=messages), 422
    elif error == 'none':
        flash('Некорректный URL', 'alert-danger')
        flash('URL обязателен', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, messages=messages), 422
    elif error == 'invalid':
        flash('Некорректный URL', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, messages=messages), 422
    else:
        site = {
            'url': url,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        conn = connect(os.getenv('DATABASE_URL'))
        add_site(site, conn)
        conn.close()
        conn = connect(os.getenv('DATABASE_URL'))
        url_id_ = get_urls_by_name(url, conn)['id']
        conn.close()
        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for('url_show', url_id_=url_id_))


@app.get('/urls')
def urls_get():
    conn = connect(os.getenv('DATABASE_URL'))
    urls = get_all_urls(conn)
    conn.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template('urls.html', urls=urls, messages=messages)


@app.route('/urls/<int:url_id_>')
def url_show(url_id_):
    try:
        conn = connect(os.getenv('DATABASE_URL'))
        url = get_urls_by_id(url_id_, conn)
        conn.close()
        conn = connect(os.getenv('DATABASE_URL'))
        checks = get_checks_by_id(url_id_, conn)
        conn.close()
        messages = get_flashed_messages(with_categories=True)
        return render_template('show_url.html', 
                                url=url, 
                                checks=checks,
                                messages=messages)


@app.post('/urls/<int:url_id_>/checks')
def url_check(url_id_):
    conn = connect(os.getenv('DATABASE_URL'))
    url = get_urls_by_id(url_id_, conn)['name']
    conn.close()
    try:
        check = get_page_content(url)
        check['url_id'] = url_id_
        check['checked_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = connect(os.getenv('DATABASE_URL'))
        add_check(check, conn)
        conn.close()
        flash('Страница успешно проверена', 'alert-success')
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
    return redirect(url_for('url_show', url_id_=url_id_))


if __name__ == '__main__':
    app.run()
