"""E2E tests: multi-step scenarios across endpoints."""

import allure
import requests


@allure.epic("Item API")
@allure.feature("E2E Scenarios")
class TestE2E:
    """End-to-end tests combining multiple API calls."""

    @allure.story("E2E")
    @allure.title("Full lifecycle: create → get → verify stats → delete")
    def test_full_item_lifecycle(self, base_url, seller_id):
        with allure.step("1. Create item"):
            payload = {
                "sellerID": seller_id,
                "name": "E2E Lifecycle Item",
                "price": 5000,
                "statistics": {"likes": 10, "viewCount": 50, "contacts": 5},
            }
            create_resp = requests.post(f"{base_url}/api/1/item", json=payload)
            assert create_resp.status_code == 200
            item_id = create_resp.json()["status"].replace("Сохранили объявление - ", "")

        with allure.step("2. Get item by ID"):
            get_resp = requests.get(f"{base_url}/api/1/item/{item_id}")
            assert get_resp.status_code == 200
            data = get_resp.json()
            item = data[0] if isinstance(data, list) else data
            assert item["name"] == "E2E Lifecycle Item"
            assert item["price"] == 5000

        with allure.step("3. Verify item in seller's list"):
            seller_resp = requests.get(f"{base_url}/api/1/{seller_id}/item")
            assert seller_resp.status_code == 200
            ids = [i["id"] for i in seller_resp.json()]
            assert item_id in ids

        with allure.step("4. Verify statistics"):
            stat_resp = requests.get(f"{base_url}/api/1/statistic/{item_id}")
            assert stat_resp.status_code == 200
            stat = stat_resp.json()
            s = stat[0] if isinstance(stat, list) else stat
            assert s["likes"] == 10
            assert s["viewCount"] == 50
            assert s["contacts"] == 5

        with allure.step("5. Delete item (API v2)"):
            del_resp = requests.delete(f"{base_url}/api/2/item/{item_id}")
            # Accept 200 or other success codes
            assert del_resp.status_code in (200, 204)

        with allure.step("6. Verify item is deleted"):
            get_after = requests.get(f"{base_url}/api/1/item/{item_id}")
            assert get_after.status_code == 404

    @allure.story("E2E")
    @allure.title("Create and retrieve multiple items for same seller")
    def test_create_multiple_retrieve_all(self, base_url, seller_id):
        created_ids = []
        names = ["Ноутбук", "Телефон", "Планшет"]

        with allure.step("Create 3 items"):
            for i, name in enumerate(names):
                resp = requests.post(f"{base_url}/api/1/item", json={
                    "sellerID": seller_id,
                    "name": name,
                    "price": (i + 1) * 1000,
                    "statistics": {"likes": i + 1, "viewCount": (i + 1) * 10, "contacts": i + 1},
                })
                assert resp.status_code == 200
                item_id = resp.json()["status"].replace("Сохранили объявление - ", "")
                created_ids.append(item_id)

        with allure.step("Get all seller items"):
            resp = requests.get(f"{base_url}/api/1/{seller_id}/item")
            assert resp.status_code == 200
            items = resp.json()

        with allure.step("Verify all created items present"):
            returned_ids = [i["id"] for i in items]
            for cid in created_ids:
                assert cid in returned_ids, f"Created item {cid} not found in seller items"

        with allure.step("Verify each item individually"):
            for item_id in created_ids:
                resp = requests.get(f"{base_url}/api/1/item/{item_id}")
                assert resp.status_code == 200

        # Cleanup
        for item_id in created_ids:
            requests.delete(f"{base_url}/api/2/item/{item_id}")

    @allure.story("E2E")
    @allure.title("Delete item removes it from seller list")
    def test_delete_removes_from_seller(self, base_url, seller_id, create_item):
        with allure.step("Create item"):
            resp, _ = create_item(seller_id=seller_id, name="Delete Test")
            item_id = resp.json()["status"].replace("Сохранили объявление - ", "")

        with allure.step("Verify item in seller list"):
            resp = requests.get(f"{base_url}/api/1/{seller_id}/item")
            ids = [i["id"] for i in resp.json()]
            assert item_id in ids

        with allure.step("Delete item"):
            del_resp = requests.delete(f"{base_url}/api/2/item/{item_id}")
            assert del_resp.status_code in (200, 204)

        with allure.step("Verify item removed from seller list"):
            resp = requests.get(f"{base_url}/api/1/{seller_id}/item")
            items = resp.json()
            ids = [i["id"] for i in items] if items else []
            assert item_id not in ids

    @allure.story("E2E — BUG")
    @allure.title("BUG: Statistics still available after item deletion")
    def test_statistics_after_delete(self, base_url, seller_id):
        """BUG: After deleting an item, its statistics are still accessible (returns 200 instead of 404)."""
        with allure.step("Create and delete item"):
            resp = requests.post(f"{base_url}/api/1/item", json={
                "sellerID": seller_id,
                "name": "Stats Delete Test",
                "price": 100,
                "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
            })
            item_id = resp.json()["status"].replace("Сохранили объявление - ", "")
            requests.delete(f"{base_url}/api/2/item/{item_id}")

        with allure.step("Verify statistics return 404"):
            stat_resp = requests.get(f"{base_url}/api/1/statistic/{item_id}")
            assert stat_resp.status_code == 404, \
                f"BUG: Statistics still available after item deletion. Got {stat_resp.status_code}"
