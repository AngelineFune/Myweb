from django.db import models
from django.contrib.auth.models import User

class Schedule(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'  
    )
    subject = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'web_schedule'

    def __str__(self):
        return f"{self.subject} - {self.date}"
    

    #history
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    date = models.DateField()
    subject = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.subject}"
