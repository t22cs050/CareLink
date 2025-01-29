from django.test import TestCase

# Create your tests here.
# tests.py

from django.urls import reverse
from careLink.models import FamilyUser  # カスタムユーザーモデルをインポート
from .models import Elder, Schedule
from datetime import date, time
from django.test import TestCase, Client
from .models import Schedule, Elder
from datetime import date
import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model



# 画面（url）遷移が正しくされるかののテスト
class ScreenTransitionTests(TestCase):
    def setUp(self):
        # FamilyUserを作成
        self.user = FamilyUser.objects.create_user(username='testuser', password='password123456789')
        self.user.elder_code = '1234'  # elder_code を手動で設定
        self.user.save()
        
    # スケジュール追加画面
    def test_add_schedule_screen(self):
        self.client.login(username='testuser', password='password123456789')  # ログイン
        response = self.client.get(reverse('careLink:add_schedule', args=['2025-01-01']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'careLink/add_schedule.html')

    # カレンダー画面
    def test_calendar_screen(self):
        self.client.login(username='testuser', password='password123456789')
        response = self.client.get(reverse('careLink:calendar', args=[2025, 1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'careLink/calender.html')

    # 高齢者の名前変更画面
    def test_change_name_screen(self):
        self.client.login(username='testuser', password='password123456789')
        response = self.client.get(reverse('careLink:change_name'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'careLink/change_name.html')

    # 高齢者のホーム画面
    def test_elder_home_screen(self):
        self.client.login(username='testuser', password='password123456789')
        response = self.client.get(reverse('careLink:elder_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'careLink/elder_home.html')
        
    # 高齢者のサインアップ画面
    def test_signup_elder_screen(self):
        self.client.login(username='testuser', password='password123456789')
        response = self.client.get(reverse('careLink:signup_elder'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'careLink/elder_add.html')

    # 家族のサインアップ画面
    def test_signup_family_screen(self):
        self.client.login(username='testuser', password='password123456789')
        response = self.client.get(reverse('careLink:signup_family'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'careLink/family_add.html')
        
# データ範囲のテスト
class ElderModelTest(TestCase):
    def test_elder_id_range(self):
        elder = Elder(elder_id=10000, elder_code=1234, elder_name="テストユーザー")
        elder.save()
        self.assertGreaterEqual(elder.elder_id, 10000)
        self.assertLessEqual(elder.elder_id, 9999999999)

    def test_elder_code_range(self):
        elder = Elder(elder_id=12345, elder_code=1000, elder_name="テストユーザー")
        elder.save()
        self.assertGreaterEqual(elder.elder_code, 1000)
        self.assertLessEqual(elder.elder_code, 9999)

    def test_elder_name_length(self):
        elder = Elder(elder_id=12345, elder_code=1234, elder_name="テスト")
        elder.save()
        self.assertLessEqual(len(elder.elder_name), 10)

    def test_elder_default_name(self):
        elder = Elder(elder_id=12345, elder_code=1234)
        elder.save()
        self.assertEqual(elder.elder_name, "ユーザー")

# スケジュールが正しく登録されるかのテスト
class ScheduleModelTest(TestCase):
    def test_action_name_length(self):
        schedule = Schedule(title="a" * 100, date=date.today(), time="12:00")
        schedule.save()
        self.assertLessEqual(len(schedule.title), 100)

    def test_date_field(self):
        schedule = Schedule(title="Test Action", date=date(2024, 1, 1), time="12:00")
        schedule.save()
        self.assertEqual(schedule.date, date(2024, 1, 1))

    def test_time_field(self):
        schedule = Schedule(title="Test Action", date=date.today(), time="12:00")
        schedule.save()
        self.assertEqual(str(schedule.time), "12:00")
        
      
class AddScheduleTestCase(TestCase):
    def setUp(self):
        """
        テスト用のクライアントと初期データを作成
        """
        self.client = Client()
        
        
        # テスト用のユーザーを作成してログイン
        self.user = FamilyUser.objects.create_user(username='testuser', password='testpassword123456')
        self.user.elder_code = '1123'  # カスタム属性を設定（もし必要であれば）
        self.user.save()
        self.client.login(username='testuser', password='testpassword123456')  # ログイン


        # テスト用のスケジュールを作成（繰り返し設定も含む）
        self.schedule1 = Schedule.objects.create(
            title="朝の体操",
            date=date(2025, 1, 1),
            sequence=1,
            recurrence="daily",  # 繰り返し設定
            completion=False,
            silver_code="1123"
        )

        self.schedule2 = Schedule.objects.create(
            title="週次ミーティング",
            date=date(2025, 1, 7),
            sequence=1,
            recurrence="weekly",
            completion=False,
            silver_code="1123"
        )

        self.add_schedule_url = reverse('careLink:add_schedule', args=["2025-01-10"])

 

    def test_existing_schedules_displayed(self):
        """
        特定の日付に登録されたスケジュールが表示されるかをテスト
        """
        response = self.client.get(reverse('careLink:add_schedule', args=["2025-01-01"]))

        # ステータスコードをチェック
        self.assertEqual(response.status_code, 200)

        # レスポンスに既存スケジュールが含まれているか確認
        self.assertContains(response, "朝の体操")
        self.assertContains(response, "daily")  # 繰り返し設定が正しく表示されるか
          
# スケジュールのテスト 
class ScheduleDeletionTestCase(TestCase):
    def setUp(self):
        # テスト用のユーザーを作成
        self.user = FamilyUser.objects.create_user(username='testuser', password='testpassword123456')
        self.client.login(username='testuser', password='testpassword123456')
        self.user.save()
        
    
    
       # Schedule オブジェクトを作成
        self.schedule = Schedule.objects.create(
            title="Test Schedule",
            date="2025-01-16",  # 日付を指定
            time="10:00",  # 時刻を指定
            recurrence="none",  # 繰り返し設定
            completion=False,  # 完了状態
            sequence=1,  # 順序
            silver_code="1234"  # 高齢者コード
        
        )

    # スケジュールの削除が正しく行われるかのテスト
    def test_schedule_deletion(self):
        # URLの解決（引数は不要）
        delete_url = reverse('careLink:delete_schedule')

        # POSTリクエストを送信（JSONデータとしてスケジュールIDを渡す）
        response = self.client.post(
            delete_url,
            json.dumps({'schedule_id': self.schedule.id}),
            content_type='application/json'
        )

        # レスポンスが成功を示すことを確認
        self.assertEqual(response.status_code, 200)

        # レスポンス内容が削除成功を示すことを確認
        self.assertJSONEqual(
            response.content,
            {'status': 'success'}
        )

        # データベースからスケジュールが削除されたことを確認
        with self.assertRaises(Schedule.DoesNotExist):
            Schedule.objects.get(id=self.schedule.id)

 
# 負荷のテスト
# class LoadTestCase(TestCase):
#     def setUp(self):
#         """テスト用のデータベースを準備"""
#         # テストデータを1000件作成
#         for i in range(1000):
#             Schedule.objects.create(
#                 title=f"Schedule {i+1}",
#                 date="2025-01-01",
#                 time="12:00",
#                 recurrence="none"
#             )
# # テストデータを1000件作成し、データベースが正しく処理するかのテスト
#     def test_bulk_schedule_creation(self):
#         """大量のスケジュールを作成し、カウントを確認"""
#         self.assertEqual(Schedule.objects.count(), 1000)

# #500件のリクエストを送信し、サーバーの応答性のテスト
#     def test_high_concurrent_requests(self):
#         url = reverse('careLink:elder_home')  # 正しいビュー名を指定
#         responses = [
#             self.client.get(url) for _ in range(10)  # 正しいHTTPメソッドを使用
#         ]
#         for response in responses:
#             self.assertEqual(response.status_code, 200)  # 200が返ることを確認




# print(reverse('careLink:delete_schedule'))