from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Poll(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    date = models.DateField(default=0)
    count = models.IntegerField(default=0)
    multi = models.BooleanField(default=False)


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    number = models.IntegerField(default=0)
    option = models.CharField(max_length=50)
    count = models.IntegerField(default=0)


class Vote(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)


CLAIM_CHOICES = [
    ('religion', 'Оскорбление чувств верующих'),
    ('info', 'Попытка выведать личную информацию'),
    ('suicide', 'Призыв к суициду'),
    ('azino', 'Реклама азартных игр'),
    ('cp', 'Детская порнография'),
    ('gov', 'Оскорбление власти'),
    ('other', 'Другое')
]


class Claim(models.Model):
    date = models.DateField()
    reason = models.CharField(
        max_length=10,
        choices=CLAIM_CHOICES
    )
    comment = models.CharField(max_length=500)
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE,
        blank=True, null=True
    )
    status = models.IntegerField(default=1)
    voteid = models.IntegerField()



class History(models.Model):
    date = models.DateField()
    time = models.TimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    log_type = models.IntegerField()
    vote_id = models.IntegerField(null=True)

