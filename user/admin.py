from django.contrib import admin
from .models import Wishlist , PurchasedGame , Review

# Register your models here.
admin.site.register(Wishlist)
admin.site.register(PurchasedGame)
admin.site.register(Review)