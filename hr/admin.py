
from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("staff", "expense_type", "amount", "created_at")
    list_filter = ("expense_type", "created_at")
    search_fields = ("staff__name", "expense_type", "remark", "description")
    ordering = ("-created_at",)
