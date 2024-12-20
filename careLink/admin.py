from django.contrib import admin
from .models import Elder
from .models import Schedule
from .models import FamilyUser

admin.site.register(Elder)
admin.site.register(FamilyUser)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    # 管理画面でどの項目を表示するか
    list_display = ('title', 'date', 'recurrence', 'completion', 'silver_code')
    
    # フィルター機能の追加
    list_filter = ('date', 'recurrence', 'completion')