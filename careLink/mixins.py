# カレンダー関連のクラスを定義するpyファイル

import calendar
from collections import deque
import datetime

# --- カレンダー関連の基底となるクラス ---
class BaseCalendarMixin:
    first_weekday = 6  # 0は月曜から、1は火曜から。6なら日曜日から。
    week_names = ['月', '火', '水', '木', '金', '土', '日']

    def setup_calendar(self):
        self._calendar = calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        """first_weekday(最初に表示される曜日)にあわせて、week_namesをシフトする"""
        week_names = deque(self.week_names)
        week_names.rotate(-self.first_weekday)
        return week_names


# --- 月間カレンダーの機能を提供するサブクラス ---
class MonthCalendarMixin(BaseCalendarMixin):
    # --- 前月を返す関数
    def get_previous_month(self, date):
        if date.month == 1:
            return date.replace(year=date.year-1, month=12, day=1)
        else:
            return date.replace(month=date.month-1, day=1)
    
    # --- 次月を返す関数
    def get_next_month(self, date):
        if date.month == 12:
            return date.replace(year=date.year+1, month=1, day=1)
        else:
            return date.replace(month=date.month+1, day=1)

    # --- その月の全ての日を返す関数
    def get_month_days(self, date):
        return self._calendar.monthdatescalendar(date.year, date.month)

    # --- 現在の月を返す関数
    def get_current_month(self):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        if month and year:
            month = datetime.date(year=int(year), month=int(month), day=1)
        else:
            month = datetime.date.today().replace(day=1)
        return month

    # --- 月間カレンダー情報の入った辞書を返す
    def get_month_calendar(self):
        self.setup_calendar()
        current_month = self.get_current_month()
        calendar_data = {
            'now': datetime.date.today(),
            'month_days': self.get_month_days(current_month),
            'month_current': current_month,
            'month_previous': self.get_previous_month(current_month),
            'month_next': self.get_next_month(current_month),
            'week_names': self.get_week_names(),
        }
        return calendar_data
