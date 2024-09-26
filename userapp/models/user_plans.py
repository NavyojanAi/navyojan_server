from navyojan.models import BaseModel

from django.db import models
from django.contrib.auth.models import User


class SubscriptionPlan(BaseModel):
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(default=365) # in days

    def __str__(self):
        return f"{self.title} - {self.amount}"

class UserPlanTracker(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='plan_tracker')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.title} - {self.end_date}"
