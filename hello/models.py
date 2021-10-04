from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField("date created", auto_now_add=True)

class PizzaOrder(models.Model):
    """Process order pizza"""
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    chat_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    cur_state = models.TextField(blank=True, null=True)
    in_progress = models.IntegerField(blank=True, null=True, db_index=True)