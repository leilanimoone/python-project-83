import os
import requests
import psycopg2
import psycopg2.extras
import datetime
from flask import (Flask,
                   request,
                   url_for,
                   flash,
                   redirect,
                   render_template)
from dotenv import load_dotenv
from urllib.parse import urlparse
from requests import ConnectionError, HTTPError
from page_analyzer.url_valid import validate_url
from page_analyzer.html import get_page_content
from page_analyzer.data import get_connection


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    with get_connection() as con:
        with con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT DISTINCT ON (urls.id) urls.id,
                                             urls.name,
                                             MAX(url_checks.created_at),
                                             url_checks.status_code
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                GROUP BY urls.id, url_checks.status_code
                ORDER BY urls.id DESC""")
            rows = cur.fetchall()
    return render_template('urls.html', checks=rows)


@app.post('/urls')
def urls_post():
    url = request.form.get('url')
    errors = validate_url(url)
    if errors:
        for error in errors:
            flash(error, 'alert alert-danger')
        return render_template('index.html', url_input=url), 422
    parsed_url = urlparse(url)
    valid_url = parsed_url.scheme + '://' + parsed_url.netloc
    with get_connection() as con:
        with con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id FROM urls
                WHERE name = %s""", [valid_url])
            result = cur.fetchone()
            if result:
                flash('Страница уже существует', 'alert alert-info')
                return redirect(url_for('url_added', id=result.id))
    with get_connection() as conn:
        with conn.cursor() as cur:
            date = datetime.date.today()
            cur.execute("""
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s) RETURNING id""", [valid_url, date])
            url_id = cur.fetchone()[0]
            conn.commit()
        flash('Страница успешно добавлена', 'alert alert-success')
        return redirect(url_for('url_added', id=url_id))


@app.route('/urls/<id>')
def url_added(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, created_at
                FROM urls
                WHERE id = %s""", [id])
            url_name, url_created_at = cur.fetchone()

    with get_connection() as con:
        with con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, created_at, status_code, h1, title, description
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC""", [id])
            rows = cur.fetchall()
        return render_template('show_url.html',
                               url_name=url_name,
                               url_id=id,
                               url_created_at=url_created_at.date(),
                               checks=rows)


@app.post('/urls/<id>/checks', methods=['POST'])
def id_check(id):
    with get_connection() as con:
        with con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT name
                FROM urls
                WHERE id = %s""", [id])
            result = cur.fetchone()

    url_name = result.name
    try:
        response = requests.get(url_name)
        response.raise_for_status()
    except (ConnectionError, HTTPError):
        flash("Произошла ошибка при проверке", "alert alert-danger")
        return redirect(url_for('url_added', id=id))

    status_code = response.status_code
    h1, title, meta = get_page_content(response.text)
    with get_connection() as conn:
        with conn.cursor() as cur:
            date = datetime.date.today()
            q_insert = """INSERT
            INTO url_checks(
                url_id,
                created_at,
                status_code,
                h1,
                title,
                description)
            VALUES (%s, %s, %s, %s, %s, %s)"""
            cur.execute(q_insert, [id, date, status_code, h1, title, meta])
            conn.commit()
    flash("Страница успешно проверена", "alert alert-success")
    return redirect(url_for('url_added', id=id))


if __name__ == '__main__':
    app.run()
