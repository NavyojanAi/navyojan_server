from userapp.models import ScholarshipData, Category, UserPreferences, UserScholarshipApplicationData
from django.contrib.auth.models import User

from django.utils import timezone
from datetime import timedelta

def perform():
    now = timezone.now()
    one_day_ago = now - timedelta(days=1)
    categories = Category.objects.all()

    for category in categories:
        scholarships = ScholarshipData.objects.filter(
            categories=category,
            datetime_created__date=one_day_ago.date()
            )
        users = User.objects.filter(
            userprofile__premium_account_privilages=True,
            category_preferences__categories=category
            )
        # user_ids = UserPreferences.objects.filter(categories=category,user__userprofile__premium_account_privilages=True).values_list('user_id', flat=True)

        # TODO: eligibility check

        final_users = users

        for scholarship in scholarships:
            for user in final_users:
                application ,created=UserScholarshipApplicationData.objects.get_or_create(
                    user=user,
                    scholarship=scholarship,
                    is_applied=True
                    )
                if not created:
                    application.is_applied=True
                    application.save()





