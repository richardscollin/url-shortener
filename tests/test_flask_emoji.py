import os
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

    # Bad way to check if it's unicode i.e. the emojis
    assert len(bytes(short_url, "utf-8")) != len(short_url)

    redirect_rv = client.get(short_url)
    assert redirect_rv.status_code == 301
    assert redirect_rv.headers.get("Location") == "https://google.com"
