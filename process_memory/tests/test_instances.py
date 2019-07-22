from flask_api import status
import pytest
import uuid


info = {
    "age": 34,
    "eyeColor": "green",
    "name": "Elena Boyd",
    "gender": "female",
    "company": "MIRACLIS"
}


@pytest.mark.parametrize("path", ["/instances/d048cbc3-2cab-4e5c-9926-d97a380388b8",
                                  "/d048cbc3-2cab-4e5c-9926-d97a380388b1/commit",
                                  "/d048cbc3-2cab-4e5c-9926-d97a380388b9/create"])
def test_create_instance(client, path):
    response = client.post(path, json=info)
    assert response.status_code == status.HTTP_201_CREATED


def test_list_instances(client):
    response = client.get("/instances")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("path", ["/instances/a59ee3fd-72bf-49cf-86d4-a9f79281c70b"])
def test_instances(client, path):
    response = client.get(path)
    assert response.status_code == status.HTTP_200_OK
