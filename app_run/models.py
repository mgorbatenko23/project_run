from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    STATUS_CHOICES = [
        ('init', 'Init'),
        ('in_progress', 'In_progress'),
        ('finished', 'Finished'),
    ]

    athlete = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name='athletes')
    comment = models.TextField()
    status = models.CharField(choices=STATUS_CHOICES, default='init')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.athlete.id} -- {self.comment} -- {self.created_at}'


class AthleteInfo(models.Model):
    user_id = models.OneToOneField(User,
                                   on_delete=models.CASCADE,
                                   related_name='athlete_info',
                                   primary_key=True)                                   
    goals = models.TextField(default='', blank=True)
    weight = models.PositiveSmallIntegerField(blank=True, null=True)