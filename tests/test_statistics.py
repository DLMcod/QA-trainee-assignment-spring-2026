"""Tests for GET /api/1/statistic/:id — Get statistics by item ID."""

import allure
import requests

from conftest import random_uuid


@allure.epic("Item API")
@allure.feature("Get Statistics")
class TestGetStatistics:
    """GET /api/1/statistic/:id"""

    @allure.story("Positive")
    @allure.title("Get statistics for existing item")
    def test_get_statistics_success(self, base_url, created_item):
        item_id, payload = created_item

        with allure.step(f"GET /api/1/statistic/{item_id}"):
            resp = requests.get(f"{base_url}/api/1/statistic/{item_id}")

        with allure.step("Verify status 200"):
            assert resp.status_code == 200

        with allure.step("Verify statistics values"):
            data = resp.json()
            stat = data[0] if isinstance(data, list) else data
            assert stat["likes"] == payload["statistics"]["likes"]
            assert stat["viewCount"] == payload["statistics"]["viewCount"]
            assert stat["contacts"] == payload["statistics"]["contacts"]

    @allure.story("Positive")
    @allure.title("Statistics contain all required fields")
    def test_statistics_fields(self, base_url, created_item):
        item_id, _ = created_item

        resp = requests.get(f"{base_url}/api/1/statistic/{item_id}")
        data = resp.json()
        stat = data[0] if isinstance(data, list) else data

        required_fields = {"likes", "viewCount", "contacts"}
        assert required_fields.issubset(stat.keys()), \
            f"Missing fields: {required_fields - set(stat.keys())}"

    @allure.story("Positive")
    @allure.title("Statistics values are integers")
    def test_statistics_types(self, base_url, created_item):
        item_id, _ = created_item

        resp = requests.get(f"{base_url}/api/1/statistic/{item_id}")
        data = resp.json()
        stat = data[0] if isinstance(data, list) else data

        assert isinstance(stat["likes"], int)
        assert isinstance(stat["viewCount"], int)
        assert isinstance(stat["contacts"], int)

    @allure.story("Negative")
    @allure.title("Get statistics for non-existent item — 404")
    def test_statistics_nonexistent(self, base_url):
        fake_id = random_uuid()
        resp = requests.get(f"{base_url}/api/1/statistic/{fake_id}")
        assert resp.status_code == 404

    @allure.story("Negative")
    @allure.title("Get statistics with invalid UUID — 400")
    def test_statistics_invalid_uuid(self, base_url):
        resp = requests.get(f"{base_url}/api/1/statistic/not-a-uuid")
        assert resp.status_code == 400

    @allure.story("Positive")
    @allure.title("Statistics match values from GET item endpoint")
    def test_statistics_consistency_with_item(self, base_url, created_item):
        """Statistics from /statistic/:id should match statistics in /item/:id."""
        item_id, _ = created_item

        with allure.step("Get item"):
            item_resp = requests.get(f"{base_url}/api/1/item/{item_id}")
            item_data = item_resp.json()
            item = item_data[0] if isinstance(item_data, list) else item_data
            item_stats = item["statistics"]

        with allure.step("Get statistics"):
            stat_resp = requests.get(f"{base_url}/api/1/statistic/{item_id}")
            stat_data = stat_resp.json()
            stat = stat_data[0] if isinstance(stat_data, list) else stat_data

        with allure.step("Compare"):
            assert stat["likes"] == item_stats["likes"]
            assert stat["viewCount"] == item_stats["viewCount"]
            assert stat["contacts"] == item_stats["contacts"]

    @allure.story("Positive")
    @allure.title("Response has correct content type")
    def test_statistics_content_type(self, base_url, created_item):
        item_id, _ = created_item
        resp = requests.get(f"{base_url}/api/1/statistic/{item_id}")
        assert "application/json" in resp.headers.get("Content-Type", "")
