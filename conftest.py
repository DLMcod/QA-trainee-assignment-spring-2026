import random
import uuid

import pytest
import requests

BASE_URL = "https://qa-internship.avito.com"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture()
def seller_id():
    """Generate a unique seller ID in the allowed range 111111–999999."""
    return random.randint(111111, 999999)


@pytest.fixture()
def create_item(base_url):
    """Factory fixture: creates an item and returns (response, payload)."""
    created_ids = []

    def _create(seller_id=None, name="Test Item", price=100, likes=1, view_count=1, contacts=1):
        if seller_id is None:
            seller_id = random.randint(111111, 999999)
        payload = {
            "sellerID": seller_id,
            "name": name,
            "price": price,
            "statistics": {
                "likes": likes,
                "viewCount": view_count,
                "contacts": contacts,
            },
        }
        resp = requests.post(f"{base_url}/api/1/item", json=payload)
        if resp.status_code == 200:
            # Extract ID from status message
            status = resp.json().get("status", "")
            item_id = status.replace("Сохранили объявление - ", "")
            created_ids.append(item_id)
        return resp, payload

    yield _create

    # Cleanup: attempt to delete created items
    for item_id in created_ids:
        try:
            requests.delete(f"{base_url}/api/2/item/{item_id}")
        except Exception:
            pass


@pytest.fixture()
def created_item(create_item):
    """Creates a single item and returns (item_id, payload)."""
    resp, payload = create_item()
    assert resp.status_code == 200
    status = resp.json()["status"]
    item_id = status.replace("Сохранили объявление - ", "")
    return item_id, payload


def random_uuid():
    return str(uuid.uuid4())
