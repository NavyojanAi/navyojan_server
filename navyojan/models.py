from django.db import models

class BaseModel(models.Model):
    datetime_modified = models.DateTimeField(auto_now=True,null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True