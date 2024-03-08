from typing import List

import requests
from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        url = f"{self.api_base_url}/processed_agent_data"
        data = [agent_data.to_dict() for agent_data in processed_agent_data_batch]
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            print("Data saved successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error saving data: {e}")
