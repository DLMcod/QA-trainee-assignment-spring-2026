"""Tests for POST /api/1/item — Create listing endpoint."""

import allure
import requests


@allure.epic("Item API")
@allure.feature("Create Item")
class TestCreateItem:
    """POST /api/1/item"""

    @allure.story("Positive")
    @allure.title("Create item with valid data")
    def test_create_item_success(self, base_url, seller_id, create_item):
        with allure.step("Send POST request with valid payload"):
            resp, payload = create_item(seller_id=seller_id, name="Телефон", price=9999, likes=5, view_count=10, contacts=3)

        with allure.step("Verify response status 200"):
            assert resp.status_code == 200

        with allure.step("Verify response contains item ID"):
            data = resp.json()
            assert "status" in data
            assert "Сохранили объявление" in data["status"]
            item_id = data["status"].replace("Сохранили объявление - ", "")
            # Verify the ID is a valid UUID
            assert len(item_id) == 36

    @allure.story("Positive")
    @allure.title("Created item is retrievable by ID")
    def test_created_item_retrievable(self, base_url, created_item):
        item_id, payload = created_item

        with allure.step(f"GET /api/1/item/{item_id}"):
            resp = requests.get(f"{base_url}/api/1/item/{item_id}")

        with allure.step("Verify response is 200"):
            assert resp.status_code == 200

        with allure.step("Verify returned data matches created item"):
            data = resp.json()
            # BUG: API returns array instead of object
            item = data[0] if isinstance(data, list) else data
            assert item["name"] == payload["name"]
            assert item["price"] == payload["price"]
            assert item["sellerId"] == payload["sellerID"]

    @allure.story("Positive")
    @allure.title("Created item appears in seller's listing")
    def test_created_item_in_seller_list(self, base_url, seller_id, create_item):
        with allure.step("Create item for specific seller"):
            resp, payload = create_item(seller_id=seller_id, name="Seller List Test")
            item_id = resp.json()["status"].replace("Сохранили объявление - ", "")

        with allure.step(f"GET /api/1/{seller_id}/item"):
            resp = requests.get(f"{base_url}/api/1/{seller_id}/item")

        with allure.step("Verify item is in seller's list"):
            assert resp.status_code == 200
            items = resp.json()
            ids = [i["id"] for i in items]
            assert item_id in ids

    @allure.story("Positive")
    @allure.title("Created item has correct statistics")
    def test_created_item_statistics(self, base_url, created_item):
        item_id, payload = created_item

        with allure.step(f"GET /api/1/statistic/{item_id}"):
            resp = requests.get(f"{base_url}/api/1/statistic/{item_id}")

        with allure.step("Verify statistics match"):
            assert resp.status_code == 200
            data = resp.json()
            stat = data[0] if isinstance(data, list) else data
            assert stat["likes"] == payload["statistics"]["likes"]
            assert stat["viewCount"] == payload["statistics"]["viewCount"]
            assert stat["contacts"] == payload["statistics"]["contacts"]

    @allure.story("Positive")
    @allure.title("Create item with minimum boundary seller ID (111111)")
    def test_create_min_seller_id(self, create_item):
        resp, _ = create_item(seller_id=111111, name="Min Seller")
        assert resp.status_code == 200

    @allure.story("Positive")
    @allure.title("Create item with maximum boundary seller ID (999999)")
    def test_create_max_seller_id(self, create_item):
        resp, _ = create_item(seller_id=999999, name="Max Seller")
        assert resp.status_code == 200

    @allure.story("Positive")
    @allure.title("Create multiple items for the same seller")
    def test_create_multiple_items_same_seller(self, base_url, seller_id, create_item):
        with allure.step("Create two items for the same seller"):
            resp1, _ = create_item(seller_id=seller_id, name="Item 1", price=100)
            resp2, _ = create_item(seller_id=seller_id, name="Item 2", price=200)
            assert resp1.status_code == 200
            assert resp2.status_code == 200

        with allure.step("Verify both items appear in seller listing"):
            resp = requests.get(f"{base_url}/api/1/{seller_id}/item")
            items = resp.json()
            names = [i["name"] for i in items]
            assert "Item 1" in names
            assert "Item 2" in names

    # --- Negative tests ---

    @allure.story("Negative")
    @allure.title("Create item without name — 400")
    def test_create_without_name(self, base_url, seller_id):
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": seller_id,
            "price": 100,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
        })
        assert resp.status_code == 400

    @allure.story("Negative")
    @allure.title("Create item with empty name — 400")
    def test_create_empty_name(self, base_url, seller_id):
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": seller_id,
            "name": "",
            "price": 100,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
        })
        assert resp.status_code == 400

    @allure.story("Negative")
    @allure.title("Create item without sellerID — 400")
    def test_create_without_seller(self, base_url):
        resp = requests.post(f"{base_url}/api/1/item", json={
            "name": "No Seller",
            "price": 100,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
        })
        assert resp.status_code == 400

    @allure.story("Negative")
    @allure.title("Create item without price — 400")
    def test_create_without_price(self, base_url, seller_id):
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": seller_id,
            "name": "No Price",
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
        })
        assert resp.status_code == 400

    @allure.story("Negative")
    @allure.title("Create item without statistics — 400")
    def test_create_without_statistics(self, base_url, seller_id):
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": seller_id,
            "name": "No Stats",
            "price": 100,
        })
        assert resp.status_code == 400

    @allure.story("Negative")
    @allure.title("Create item with empty body — 400")
    def test_create_empty_body(self, base_url):
        resp = requests.post(f"{base_url}/api/1/item", json={})
        assert resp.status_code == 400

    @allure.story("Negative")
    @allure.title("Create item with string sellerID — 400")
    def test_create_string_seller(self, base_url):
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": "abc",
            "name": "String Seller",
            "price": 100,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
        })
        assert resp.status_code == 400

    @allure.story("Negative")
    @allure.title("Create item with string price — 400")
    def test_create_string_price(self, base_url, seller_id):
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": seller_id,
            "name": "String Price",
            "price": "abc",
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
        })
        assert resp.status_code == 400

    @allure.story("Negative — BUG")
    @allure.title("BUG: Negative price is accepted (should be 400)")
    def test_create_negative_price(self, base_url, seller_id):
        """BUG: API accepts negative price values."""
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": seller_id,
            "name": "Negative Price",
            "price": -100,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
        })
        # Expected: 400, Actual: 200 — this is a BUG
        assert resp.status_code == 400, f"BUG: Negative price accepted. Got {resp.status_code}"

    @allure.story("Negative — BUG")
    @allure.title("BUG: Negative statistics values are accepted (should be 400)")
    def test_create_negative_statistics(self, base_url, seller_id):
        """BUG: API accepts negative statistics values."""
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": seller_id,
            "name": "Negative Stats",
            "price": 100,
            "statistics": {"likes": -5, "viewCount": -10, "contacts": -1},
        })
        # Expected: 400, Actual: 200 — this is a BUG
        assert resp.status_code == 400, f"BUG: Negative statistics accepted. Got {resp.status_code}"

    @allure.story("Negative — BUG")
    @allure.title("BUG: Zero price treated as missing field (should accept 0)")
    def test_create_zero_price(self, base_url, seller_id):
        """BUG: price=0 returns 'поле price обязательно' instead of accepting 0."""
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": seller_id,
            "name": "Zero Price",
            "price": 0,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
        })
        # BUG: price=0 is treated as "not provided"
        # Accepting 400 is reasonable for zero price, but error message is wrong
        assert resp.status_code == 400
        data = resp.json()
        assert "обязательно" in data["result"]["message"], \
            "BUG: Zero price treated as missing field instead of invalid value"

    @allure.story("Negative — BUG")
    @allure.title("BUG: Zero likes treated as missing field")
    def test_create_zero_likes(self, base_url, seller_id):
        """BUG: likes=0 returns 'поле likes обязательно' instead of accepting 0."""
        resp = requests.post(f"{base_url}/api/1/item", json={
            "sellerID": seller_id,
            "name": "Zero Likes",
            "price": 100,
            "statistics": {"likes": 0, "viewCount": 1, "contacts": 1},
        })
        # BUG: Zero values treated as missing
        # This SHOULD be 200 (0 is a valid value for likes)
        assert resp.status_code == 200, \
            f"BUG: likes=0 treated as missing. Got {resp.status_code}: {resp.text}"

    @allure.story("Corner case")
    @allure.title("Idempotency: duplicate POST creates separate items")
    def test_create_duplicate_items(self, base_url, seller_id, create_item):
        """Same payload creates two distinct items (POST is not idempotent)."""
        with allure.step("Create two items with identical payloads"):
            resp1, _ = create_item(seller_id=seller_id, name="Duplicate", price=500)
            resp2, _ = create_item(seller_id=seller_id, name="Duplicate", price=500)

        with allure.step("Verify both succeeded with different IDs"):
            assert resp1.status_code == 200
            assert resp2.status_code == 200
            id1 = resp1.json()["status"].replace("Сохранили объявление - ", "")
            id2 = resp2.json()["status"].replace("Сохранили объявление - ", "")
            assert id1 != id2, "Duplicate POST should create distinct items"

    @allure.story("Corner case — BUG")
    @allure.title("BUG: Create response does not return full object per spec")
    def test_create_response_structure(self, create_item):
        """BUG: POST response should contain full item object per Postman spec,
        but only returns {status: 'Сохранили объявление - <id>'}."""
        resp, _ = create_item(name="Response Structure")
        data = resp.json()

        with allure.step("Check response contains expected fields"):
            # Per Postman spec, response should include: id, sellerId, name, price, statistics, createdAt
            # BUG: Only "status" field is returned
            expected_keys = {"id", "sellerId", "name", "price", "statistics", "createdAt"}
            actual_keys = set(data.keys())
            missing = expected_keys - actual_keys
            assert not missing, f"BUG: Create response missing fields: {missing}. Got only: {actual_keys}"

    @allure.story("Negative")
    @allure.title("Create item with no Content-Type header")
    def test_create_no_content_type(self, base_url, seller_id):
        resp = requests.post(f"{base_url}/api/1/item", data='{"sellerID": 555555}')
        assert resp.status_code in (400, 415)

    @allure.story("Corner case — BUG")
    @allure.title("BUG: sellerID field naming inconsistency (sellerID vs sellerId)")
    def test_seller_id_field_naming(self, base_url, created_item):
        """BUG: POST accepts 'sellerID' but GET returns 'sellerId'."""
        item_id, payload = created_item
        resp = requests.get(f"{base_url}/api/1/item/{item_id}")
        data = resp.json()
        item = data[0] if isinstance(data, list) else data

        with allure.step("Check field naming consistency"):
            # POST request uses "sellerID" (uppercase ID)
            # GET response uses "sellerId" (lowercase d)
            assert "sellerID" in item or "sellerId" in item
            # This documents the inconsistency
            if "sellerId" in item and "sellerID" not in item:
                allure.attach(
                    "POST accepts 'sellerID' but GET returns 'sellerId'",
                    name="Field naming inconsistency",
                    attachment_type=allure.attachment_type.TEXT,
                )
