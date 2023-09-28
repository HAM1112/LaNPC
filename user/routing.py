from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('user/chat/<int:game_id>/', consumers.ChatConsumer.as_asgi()),
    
    
]