from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from app_run import utils


class Run(models.Model):
    """ Забег """
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
    distance = models.FloatField(blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)    
    run_time_seconds = models.IntegerField(blank=True, default=0)
    speed = models.FloatField(blank=True, default=0)

    def get_total_distance(self):
        coordinates = [(obj.latitude, obj.longitude) for obj in self.positions.all()]
        return utils.get_distance_in_km(coordinates)

    def __str__(self):
        return f'run: {self.id}, {self.athlete.id}: {self.athlete.username}, STATUS {self.status}'


class AthleteInfo(models.Model):
    """ дополнительная информация об атлете """
    athlete = models.OneToOneField(User,
                                   on_delete=models.CASCADE,
                                   related_name='athlete_info',
                                   primary_key=True)                                   
    goals = models.TextField(default='', blank=True)
    weight = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.athlete.id}: {self.athlete.username}, weight {self.weight}'


class Challenge(models.Model):
    """ Челенджи """
    athlete = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name='challenges')
    full_name = models.CharField()

    def __str__(self):
        # return f'{self.athlete.id}: {self.athlete.username}, full_name {self.full_name}'
        return f'{self.athlete_id}: full_name {self.full_name}'


class Position(models.Model):
    """ Координаты атлета """
    run = models.ForeignKey(Run,
                            on_delete=models.CASCADE,
                            related_name='positions')
    latitude = models.DecimalField(max_digits=6, decimal_places=4,
                                   validators=[MinValueValidator(-90),
                                               MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=7,
                                    decimal_places=4,
                                    validators=[MinValueValidator(-180),
                                                MaxValueValidator(180)])
    date_time = models.DateTimeField(blank=True, null=True)
    speed = models.FloatField(blank=True, default=0)
    distance = models.FloatField(blank=True, default=0)

    def __str__(self):
        return (f'run: {self.run.id}, {self.run.athlete.id}: {self.run.athlete.username}, '
                f'latitude {self.latitude}, longitude {self.longitude}, ')


class CollectibleItem(models.Model):
    """ Коллекция предметов(артефакты) собираемые атлетом """
    user = models.ManyToManyField(User,
                                  blank=True,                                  
                                  related_name='items')
    name = models.CharField()
    uid = models.CharField()
    latitude = models.FloatField(validators=[MinValueValidator(-90.0),
                                             MaxValueValidator(90.0)
                                             ])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0),
                                              MaxValueValidator(180.0)])
    picture = models.URLField()
    value = models.IntegerField()    

    def __str__(self):
        return (f'name {self.name}, '
                f'latitude {self.latitude}, longitude {self.longitude}')


class Subscribe(models.Model):
    """ Подписки атлетов на тренера(ов) """
    athlete = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name='subscribes_athlete')
    coach = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='subscribes_coach')
    rating = models.IntegerField(blank=True,
                                 null=True,
                                 validators=[MinValueValidator(1),
                                             MaxValueValidator(5)])
    class Meta:
        unique_together = ['athlete', 'coach']

    def __str__(self):
        return (f'{self.athlete_id}: {self.athlete.username}, '
                f'{self.coach_id}: {self.coach.username}, rating {self.rating}')