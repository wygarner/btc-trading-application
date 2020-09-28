from django.db import models

class Bot(models.Model):
    key = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)
    confidence = models.CharField(max_length=100)
    risk = models.CharField(max_length=100)
    reward = models.CharField(max_length=100)
    test = models.CharField(max_length=100)