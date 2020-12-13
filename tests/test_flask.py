import pytest
from bs4 import BeautifulSoup
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_add_url(client):
    root_rv = client.get('/')
    assert root_rv.status_code == 200

    post_rv = client.post('/', data=dict(url="https://google.com"))

    soup = BeautifulSoup(post_rv.data, 'html.parser')
    short_url = soup.find(id="result-link")['href']

    redirect_rv = client.get(short_url)
    assert redirect_rv.status_code == 301
    assert redirect_rv.headers.get("Location") == "https://google.com"

def test_double_add_url(client):
    root_rv = client.get('/')
    assert root_rv.status_code == 200

    post_rv = client.post('/', data=dict(url="http://neverssl.com"))
    soup = BeautifulSoup(post_rv.data, 'html.parser')
    short_url1 = soup.find(id="result-link")['href']

    redirect_rv = client.get(short_url1)
    assert redirect_rv.status_code == 301
    assert redirect_rv.headers.get("Location") == "http://neverssl.com"

    post_rv = client.post('/', data=dict(url="neverssl.com"))
    soup = BeautifulSoup(post_rv.data, 'html.parser')
    short_url2 = soup.find(id="result-link")['href']
   
    redirect_rv = client.get(short_url2)
    assert redirect_rv.status_code == 301
    assert redirect_rv.headers.get("Location") == "http://neverssl.com"


def test_add_url_no_http(client):
    root_rv = client.get('/')
    assert root_rv.status_code == 200

    post_rv = client.post('/', data=dict(url="google.com"))
    assert post_rv.status_code == 200

    soup = BeautifulSoup(post_rv.data, 'html.parser')
    short_url = soup.find(id="result-link")['href']

    redirect_rv = client.get(short_url)
    assert redirect_rv.status_code == 301
    assert redirect_rv.headers.get("Location") == "http://google.com"


def test_add_bad_url(client):
    post_rv = client.post('/', data=dict(url="Hello World"))
    assert b"Invalid url" in post_rv.data

def test_add_localhost(client):
    post_rv = client.post('/', data=dict(url="localhost"))
    assert b"Invalid url" in post_rv.data

    post_rv = client.post('/', data=dict(url="localhost:3000"))
    assert b"Invalid url" in post_rv.data

def test_add_ipv4(client):
    post_rv = client.post('/', data=dict(url="8.8.8.8"))
    assert b"Invalid url" in post_rv.data
