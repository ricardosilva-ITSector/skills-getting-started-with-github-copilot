from fastapi.testclient import TestClient
from urllib.parse import quote
import copy

from src.app import app as fastapi_app
import src.app as app_module

client = TestClient(fastapi_app)


import pytest


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_duplicate():
    activity = "Chess Club"
    email = "testuser@example.com"
    url = f"/activities/{quote(activity)}/signup?email={email}"

    # First signup should succeed
    r1 = client.post(url)
    assert r1.status_code == 200
    assert "Signed up" in r1.json().get("message", "")

    # Duplicate signup should fail with 400
    r2 = client.post(url)
    assert r2.status_code == 400


def test_unregister():
    activity = "Chess Club"
    email = "to_remove@example.com"
    signup_url = f"/activities/{quote(activity)}/signup?email={email}"
    del_url = f"/activities/{quote(activity)}/participants?email={email}"

    r = client.post(signup_url)
    assert r.status_code == 200

    r = client.delete(del_url)
    assert r.status_code == 200

    # Ensure participant removed
    r = client.get("/activities")
    data = r.json()
    assert email not in data[activity]["participants"]
