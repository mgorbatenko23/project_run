from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    athlete = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name='athletes')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.athlete.id} -- {self.comment} -- {self.created_at}'