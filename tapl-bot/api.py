import json
import urllib3
import time


class APIInstance:
    def __init__(self):
        self.http = urllib3.PoolManager()
        self.base_url = "http://localhost:8000"

    def __post_request(self, append_url, data={}):
        url = f"{self.base_url}/{append_url}"
        encoded_data = json.dumps(data).encode("utf-8")
        response = self.http.request(
            "POST", url, body=encoded_data, headers={"Content-Type": "application/json"}
        )
        response_data = json.loads(response.data.decode("utf-8"))
        return {"status": response.status, "data": response_data}

    def __get_request(self, append_url, params={}):
        url = f"{self.base_url}/{append_url}?"
        for key, value in params.items():
            url += f"{key}={value}&"
        url += f"nonce={time.time()}"
        response = self.http.request(
            "GET",
            url,
            headers={"Content-Type": "application/json", "Cache-Control": "max-age=0"},
        )
        response_data = json.loads(response.data.decode("utf-8"))
        return {"status": response.status, "data": response_data}

    def get_number_login_code(self, user_id, number_id):
        res = self.__get_request(
            "number_login_code", {"user_id": user_id, "number_id": number_id}
        )
        if res["status"] == 200:
            return str(res["data"]["code"])
        else:
            return "0"

    def get_all_lend_numbers(self, user_id):
        res = self.__get_request("lent_nfts", {"user_id": user_id})

        if res["status"] == 200:
            return res["data"]
        else:
            return []

    def get_all_borrowed_numbers(self, user_id):
        res = self.__get_request("borrowed_nfts", {"user_id": user_id})

        if res["status"] == 200:
            return res["data"]
        else:
            return []

    def get_market_quotes(self):
        res = self.__get_request("configs")

        if res["status"] == 200:
            return res["data"]
        else:
            return {}

    def get_all_own_numbers(self, user_address):
        res = self.__get_request("own_nfts", {"user_address": user_address})

        if res["status"] == 200:
            return res["data"]
        else:
            return {}

    def do_lend_number(self, user_id, number_address):
        res = self.__post_request(
            "lend_nft", {"user_id": user_id, "nft_address": number_address}
        )

        if res["status"] == 200:
            return res["data"]
        else:
            return {}

    def get_storage_wallet_address(self):
        res = self.__get_request("storage_wallet_address")

        if res["status"] == 200:
            return res["data"]["address"]
        else:
            return "0:00000000000000000000000"

    def get_number(self, number_id):
        res = self.__get_request("nft", {"nft_id": number_id})

        if res["status"] == 200:
            return res["data"]
        else:
            return {}

    def get_orders_by_number_id(self, number_id):
        res = self.__get_request("orders", {"nft_id": number_id})

        if res["status"] == 200:
            return res["data"]
        else:
            return []

    def get_borrow_payment_url(self, user_id):
        res = self.__post_request("borrow_nft", {"user_id": user_id})

        if res["status"] == 200:
            return res["data"]["url"]
        else:
            return ""

    def get_takeback_payment_url(self, user_id, number_id):
        res = self.__post_request(
            "take_back_nft", {"nft_id": number_id, "user_id": user_id}
        )

        if res["status"] == 200:
            return res["data"]["url"]
        else:
            return ""
