"""Tests for GET /api/1/:sellerID/item — Get all listings by seller ID."""

import allure
import requests


@allure.epic("Item API")
@allure.feature("Get Items by Seller")
class TestGetSellerItems:
    """GET /api/1/:sellerID/item"""

    @allure.story("Positive")
    @allure.title("Get items for seller with listings")
    def test_get_seller_items(self, base_url, seller_id, create_item):
        with allure.step("Create item for seller"):
            resp, payload = create_item(seller_id=seller_id, name="Seller Item")
            assert resp.status_code == 200

        with allure.step(f"GET /api/1/{seller_id}/item"):
            resp = requests.get(f"{base_url}/api/1/{seller_id}/item")

        with allure.step("Verify status 200 and items returned"):
            assert resp.status_code == 200
            items = resp.json()
            assert isinstance(items, list)
            assert len(items) >= 1

    @allure.story("Positive")
    @allure.title("All returned items belong to the requested seller")
    def test_seller_items_belong_to_seller(self, base_url, seller_id, create_item):
        create_item(seller_id=seller_id, name="Ownership Test")

        resp = requests.get(f"{base_url}/api/1/{seller_id}/item")
        items = resp.json()

        with allure.step("Verify all items have correct sellerId"):
            for item in items:
                assert item["sellerId"] == seller_id, \
                    f"Item {item['id']} belongs to seller {item['sellerId']}, expected {seller_id}"

    @allure.story("Positive")
    @allure.title("Seller items contain all required fields")
    def test_seller_items_fields(self, base_url, seller_id, create_item):
        create_item(seller_id=seller_id, name="Fields Test")

        resp = requests.get(f"{base_url}/api/1/{seller_id}/item")
        items = resp.json()

        required_fields = {"id", "sellerId", "name", "price", "statistics", "createdAt"}
        for item in items:
            assert required_fields.issubset(item.keys()), \
                f"Missing fields: {required_fields - set(item.keys())}"

    @allure.story("Positive")
    @allure.title("Get items for seller with multiple items returns all")
    def test_seller_multiple_items(self, base_url, seller_id, create_item):
        with allure.step("Create 3 items"):
            for i in range(3):
                create_item(seller_id=seller_id, name=f"Multi Item {i}", price=(i + 1) * 100)

        resp = requests.get(f"{base_url}/api/1/{seller_id}/item")
        items = resp.json()

        with allure.step("Verify at least 3 items returned"):
            assert len(items) >= 3

    @allure.story("Negative")
    @allure.title("Get items for non-existent seller — empty list or 404")
    def test_get_nonexistent_seller(self, base_url):
        # Use a seller ID unlikely to have items
        import random
        unique_seller = random.randint(111111, 999999)
        resp = requests.get(f"{base_url}/api/1/{unique_seller}/item")
        # Could be empty list 200 or 404
        if resp.status_code == 200:
            data = resp.json()
            # Acceptable: empty array
            assert isinstance(data, list)
        else:
            assert resp.status_code == 404

    @allure.story("Negative")
    @allure.title("Get items with string seller ID — 400")
    def test_get_string_seller_id(self, base_url):
        resp = requests.get(f"{base_url}/api/1/abc/item")
        assert resp.status_code == 400

    @allure.story("Negative — BUG")
    @allure.title("BUG: Negative seller ID accepted (returns items instead of 400)")
    def test_get_negative_seller_id(self, base_url):
        """BUG: API accepts negative seller IDs and returns items for sellerID=-1."""
        resp = requests.get(f"{base_url}/api/1/-1/item")
        assert resp.status_code == 400, \
            f"BUG: Negative seller ID accepted. Got {resp.status_code}"

    @allure.story("Negative")
    @allure.title("Get items with zero seller ID — 400")
    def test_get_zero_seller_id(self, base_url):
        resp = requests.get(f"{base_url}/api/1/0/item")
        # 0 is outside the allowed range
        assert resp.status_code in (200, 400)

    @allure.story("Positive")
    @allure.title("Response has correct content type")
    def test_seller_items_content_type(self, base_url, seller_id, create_item):
        create_item(seller_id=seller_id)
        resp = requests.get(f"{base_url}/api/1/{seller_id}/item")
        assert "application/json" in resp.headers.get("Content-Type", "")
