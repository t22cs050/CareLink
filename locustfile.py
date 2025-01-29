from locust import HttpUser, task, between
from requests.auth import HTTPBasicAuth

class CareLinkUser(HttpUser):
    wait_time = between(1, 5)  # 各タスクの間の待機時間を1秒から5秒の間でランダムに設定



    
    @task
    def view_top(self):
        # Basic認証を通過するため、以下を記述する
        auth = HTTPBasicAuth(username="username", password="password123456")
        self.client.get("/careLink/login") #どうせつ５０００にんかのう
   
   #以下にほかのページの負荷テストを書き入れる