from flask_api import status


def test_hello(client):
    """
    Test app is initializing
    """
    response = client.get("/hello")
    assert response.data == b"Hello, World!"


def test_response(client):
    """
    Teste app root
    """
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
