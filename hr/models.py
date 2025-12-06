from django.db import models

EXPENSE_TYPES = [
    ("Travel", "Travel"),
    ("Food", "Food"),
    ("Office Stationary", "Office Stationary"),
    ("Fuel", "Fuel"),
    ("Misc", "Misc"),
    ("Online E-commerce", "Online E-commerce"),
    ("Accommodation", "Accommodation"),
]

class Expense(models.Model):
    staff = models.ForeignKey("leads.Staff", on_delete=models.CASCADE, related_name="staff_expenses")
    expense_type = models.CharField(max_length=100, choices=EXPENSE_TYPES)
    remark = models.TextField(blank=True, null=True)
    bill_image = models.ImageField(upload_to='staff_bills/', blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff.name} - {self.expense_type}"
