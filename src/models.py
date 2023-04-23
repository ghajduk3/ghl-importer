from django.db import models


class LoanPool(models.Model):
    status = models.PositiveSmallIntegerField(null=False)
    status_name = models.CharField(max_length=255, null=True)
    payload = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "src"
        db_table = "ghl_loandatapool"


class Contact(models.Model):
    contact_id = models.CharField(unique=True, max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "src"
        db_table = "ghl_contact"


class ContactHistory(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, null=False)
    pool = models.ForeignKey(LoanPool, on_delete=models.PROTECT, null=False)
    action = models.PositiveSmallIntegerField(null=False)
    action_name = models.CharField(max_length=255, null=False)
    action_data = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "src"
        db_table = "ghl_contact_history"
