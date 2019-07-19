from flask_api import status
import pytest
import uuid

def test_list_instances(client):
    response = client.get("/instances")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("path", ("/instances/a59ee3fd-72bf-49cf-86d4-a9f79281c70b"))
def test_instances(client, path):
    response = client.get(path)
    assert response.status_code == status.HTTP_200_OK

"""
def test_create_instance(client):
    import pdb; pdb.set_trace()
    new_uuid = uuid.uuid5()
    uri = f"/instances/"
    response = client.post(uri)
"""