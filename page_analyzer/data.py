import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from psycopg2 import connect


load_dotenv()


def get_connection():
    return connect(os.getenv('DATABASE_URL'))


def close(conn):
    conn.close()


def commit_db(conn):
    conn.commit()


def add_check(check, conn):
    with conn.cursor() as cur:
        q_insert = '''INSERT
        INTO url_checks(
            url_id,
            status_code,
            h1,
            title,
            description,
            created_at)
        VALUES (%s, %s, %s, %s, %s, %s)'''
        cur.execute(q_insert, (
            check['url_id'],
            check['status_code'],
            check['h1'],
            check['title'],
            check['description'],
            check['checked_at']
        ))
        commit_db(conn)


def get_checks_by_id(url_id_, conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q_select = '''SELECT *
        FROM url_checks
        WHERE url_id=(%s)
        ORDER BY id DESC'''
        cur.execute(q_select, [url_id_])
        checks = cur.fetchall()
    return checks


def get_urls_by_name(name, conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q_select = '''SELECT *
        FROM urls WHERE name=(%s)'''
        cur.execute(q_select, [name])
        urls = cur.fetchone()
    return urls


def add_site(site, conn):
    with conn.cursor() as cur:
        q_insert = '''INSERT
        INTO urls (name, created_at)
        VALUES (%s, %s)'''
        cur.execute(q_insert, (
            site['url'],
            site['created_at']
        ))
        commit_db(conn)


def get_all_urls(conn):
    conn.autocommit = True
    curs = conn.cursor(cursor_factory=RealDictCursor)
    curs.execute("""
    SELECT DISTINCT ON (id) *
    FROM urls
    LEFT JOIN (
    SELECT
        url_id,
        status_code,
        created_at AS last_check
    FROM url_checks
    ORDER BY id DESC
    ) AS checks ON urls.id = checks.url_id
    ORDER BY id DESC
    """)
    data_urls = curs.fetchall()
    return data_urls


def get_urls_by_id(url_id_, conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q_select = '''SELECT *
        FROM urls WHERE id=(%s)'''
        cur.execute(q_select, [url_id_])
        urls = cur.fetchone()
    return urls
