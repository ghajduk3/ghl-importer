from django.urls import path
from src.api import views as api_views

urlpatterns = [
    path(
        "loan-data-pool",
        api_views.LoanDataPool.as_view(),
        name="ghl.loan_data_pool",
    ),
]