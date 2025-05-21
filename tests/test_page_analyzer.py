import pytest
from page_analyzer.app import app

@pytest.fixture 
def client(): 
    app.config['TESTING'] = True 
    return app.test_client()

def test_main_page(client): 
    response = client.get('/') 
    assert response.status_code == 200

def test_urls_post_valid(client): 
    response = client.post('/urls', data={'url':''})
    assert response.status_code == 302
