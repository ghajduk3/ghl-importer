from django.db import models


class LoanPool(models.Model):
    loan_id = models.IntegerField(null=True)
    status = models.PositiveSmallIntegerField(null=False)
    status_name = models.CharField(max_length=255, null=True)
    payload = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "src"
        db_table = "ghl_loandatapool"
