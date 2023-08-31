from django.contrib import admin
from .models import Wishlist , PurchasedGame

# Register your models here.
admin.site.register(Wishlist)
admin.site.register(PurchasedGame)