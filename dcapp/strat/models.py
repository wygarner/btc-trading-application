from django.db import models

class Strategy(models.Model):
    confidence = models.TextField()
    risk = models.TextField()
    reward = models.TextField()
