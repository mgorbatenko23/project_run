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
    distance = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)    

    def __str__(self):
        return f'{self.athlete.id} -- {self.comment} -- {self.created_at}'


class AthleteInfo(models.Model):
    athlete = models.OneToOneField(User,
                                   on_delete=models.CASCADE,
                                   related_name='athlete_info',
                                   primary_key=True)                                   
    goals = models.TextField(default='', blank=True)
    weight = models.PositiveSmallIntegerField(blank=True, null=True)


class Challenge(models.Model):
    athlete = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name='challenges')
    full_name = models.CharField()


class Position(models.Model):
    run = models.ForeignKey(Run,
                            on_delete=models.CASCADE,
                            related_name='positions')
    latitude = models.DecimalField(max_digits=6, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)

    def __str__(self):
        return f'latitude: {self.latitude}, longitude: {self.longitude}'