from random import choice
from locust import HttpUser, between, task

class AssetBrowserUser(HttpUser):
    wait_time = between(1, 5)
    def on_start(self):
        response = self.client.get("/marketplace/assets/",name="/marketplace/assets/")
        response.raise_for_status()
        self.asset_ids = [asset["id"] for asset in response.json()["results"]]

    @task(3)
    def browse_assets(self):
        self.client.get("/marketplace/assets/",name="/marketplace/assets/")
        
    @task(4)
    def view_asset(self):
        asset_id = choice(self.asset_ids)
        self.client.get(f"/marketplace/assets/{asset_id}/",name="/marketplace/assets/:id/")

    @task(2)
    def search_assets(self):
        self.client.get("/marketplace/assets/?search=python",name="/marketplace/assets/?search=:term")
