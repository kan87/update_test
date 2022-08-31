from django.db import models

# Create your models here.

class Pilot(models.Model):
    e_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    extra = models.CharField(max_length=50)
    extra_locked = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.first_name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class PendingPilot(models.Model):
    e_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    extra = models.CharField(max_length=50)
    approved = models.BooleanField('Approved', default=False)

    def __str__(self):
        return self.first_name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)