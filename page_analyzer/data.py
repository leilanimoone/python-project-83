from psycopg2.extras import RealDictCursor


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
        conn.commit()


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
        cur.execute('''SELECT * FROM urls WHERE name=(%s)''', [name])
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
        conn.commit()


def get_all_urls(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
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
        data_urls = cur.fetchall()
    return data_urls


def get_urls_by_id(url_id_, conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('''SELECT * FROM urls WHERE id=(%s)''', [url_id_])
        urls = cur.fetchone()
    return urls
