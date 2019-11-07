import pytest
from flask_api import status

with open('process_memory.json', 'r') as memory_file:
    info = memory_file.read()


@pytest.mark.parametrize("path", ["/memory/d048cbc3-2cab-4e5c-9926-d97a38038888"])
def test_create_memory(client, path):
    response = client.post(path, json=info)
    assert response.status_code == status.HTTP_201_CREATED