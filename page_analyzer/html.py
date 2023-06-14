from bs4 import BeautifulSoup


def get_url_data(page_data):
    soup = BeautifulSoup(page_data, 'html.parser')
    h1 = soup.find('h1').get_text() if soup.find('h1') else ''
    title = soup.find('title').get_text() if soup.find('title') else ''
    meta = soup.find(
        'meta', {"name": "description"}).attrs['content'] if soup.find(
        'meta', {"name": "description"}) else ''
    return h1, title, meta
