"""Tests for GET /api/1/item/:id — Get listing by ID endpoint."""

import allure
import requests

from conftest import random_uuid


@allure.epic("Item API")
@allure.feature("Get Item by ID")
class TestGetItemById:
    """GET /api/1/item/:id"""

    @allure.story("Positive")
    @allure.title("Get existing item by ID returns correct data")
    def test_get_existing_item(self, base_url, created_item):
        item_id, payload = created_item

        with allure.step(f"GET /api/1/item/{item_id}"):
            resp = requests.get(f"{base_url}/api/1/item/{item_id}")

        with allure.step("Verify status 200"):
            assert resp.status_code == 200

        with allure.step("Verify item fields"):
            data = resp.json()
            item = data[0] if isinstance(data, list) else data
            assert item["id"] == item_id
            assert item["name"] == payload["name"]
            assert item["price"] == payload["price"]

    @allure.story("Positive")
    @allure.title("Get item response contains all required fields")
    def test_get_item_all_fields(self, base_url, created_item):
        item_id, _ = created_item

        resp = requests.get(f"{base_url}/api/1/item/{item_id}")
        data = resp.json()
        item = data[0] if isinstance(data, list) else data

        with allure.step("Verify all fields present"):
            required_fields = {"id", "sellerId", "name", "price", "statistics", "createdAt"}
            assert required_fields.issubset(item.keys()), \
                f"Missing fields: {required_fields - set(item.keys())}"

        with allure.step("Verify statistics subfields"):
            stat_fields = {"likes", "viewCount", "contacts"}
            assert stat_fields.issubset(item["statistics"].keys())

    @allure.story("Positive")
    @allure.title("Get item response has correct content type")
    def test_get_item_content_type(self, base_url, created_item):
        item_id, _ = created_item
        resp = requests.get(f"{base_url}/api/1/item/{item_id}")
        assert "application/json" in resp.headers.get("Content-Type", "")

    @allure.story("Negative")
    @allure.title("Get non-existent item — 404")
    def test_get_nonexistent_item(self, base_url):
        fake_id = random_uuid()
        resp = requests.get(f"{base_url}/api/1/item/{fake_id}")
        assert resp.status_code == 404

    @allure.story("Negative")
    @allure.title("Get item with invalid UUID — 400")
    def test_get_invalid_uuid(self, base_url):
        resp = requests.get(f"{base_url}/api/1/item/not-a-uuid")
        assert resp.status_code == 400

    @allure.story("Negative")
    @allure.title("Get item with empty ID — 400 or 404")
    def test_get_empty_id(self, base_url):
        resp = requests.get(f"{base_url}/api/1/item/")
        assert resp.status_code in (400, 404, 405)

    @allure.story("Corner case — BUG")
    @allure.title("BUG: GET /item/:id returns array instead of single object")
    def test_get_item_returns_single_object(self, base_url, created_item):
        """BUG: Response should be a single JSON object, but returns an array."""
        item_id, _ = created_item

        resp = requests.get(f"{base_url}/api/1/item/{item_id}")
        data = resp.json()

        with allure.step("Verify response is object, not array"):
            assert isinstance(data, dict), \
                f"BUG: GET /item/:id returns {type(data).__name__} instead of dict. Response: {data}"

    @allure.story("Positive")
    @allure.title("Get item — createdAt field is present and non-empty")
    def test_get_item_created_at(self, base_url, created_item):
        item_id, _ = created_item
        resp = requests.get(f"{base_url}/api/1/item/{item_id}")
        data = resp.json()
        item = data[0] if isinstance(data, list) else data
        assert item.get("createdAt"), "createdAt should be present and non-empty"
