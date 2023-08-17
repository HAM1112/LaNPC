from django.db import models

# Create your models here.
from django.db import models

# Create your models here.

class Category(models.Model):
    
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Game(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    coins = models.PositiveIntegerField()
    time_of_creation = models.DateTimeField(auto_now_add=True)
    banner_image = models.ImageField(upload_to='game_banners/' , null=True)
    cover_image = models.ImageField(upload_to='game_covers/', null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name