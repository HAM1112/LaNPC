from channels.consumer import AsyncConsumer 
from channels.db import database_sync_to_async 
import json , re
from account.models import User
from adminpanel.models import Game
from .models import Message
from asgiref.sync import sync_to_async
# from django.contrib.auth import get_user_model


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connect' , event)
        user = self.scope['user']
        
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        match = re.search(r"game_id=([^&]+)", query_string)
        if match:
            game_id = match.group(1)
        else:
            # Handle the case where game_id is not found in the query parameters
            game_id = None
            
        chat_room = f"user_chatroom_{game_id}"
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type' : 'websocket.accept',
        })
        
    async def websocket_receive(self, event):
        print('recevie' , event)
        received_data = json.loads(event['text'])
        msg = received_data.get('message')
        send_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('sent_to')
        # message = self.create_message(send_by_id, send_to_id, msg)
        if not msg:
            print("eroor : empty message")
            return False
        
        sent_by_user = await self.get_user_object(send_by_id)
        sent_to_game = await self.get_game_object(send_to_id)
        if not sent_by_user:
            print("Error : sent by user is incorrect")
        if not sent_to_game:
            print("Error : send to user is incorrect")
            
        message = await self.create_message(send_by_id, send_to_id, msg)
        
        other_user_chat_room = f"user_chatroom_{send_to_id}"
        self_user = self.scope['user']
         
        response = {
            'message' : msg,
            'send_by' : self_user.id,
            'send_by_name' : self_user.username
            
        }
        
        # await self.channel_layer.group_send(
        #     other_user_chat_room,
        #     {
        #         'type' : 'chat_message',
        #         'text' : json.dumps(response)
        #     }
        # )
        
        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type' : 'chat_message',
                'text' : json.dumps(response)
            }
        )
        # await self.send({
        #     'type' : 'websocket.send',
        #     'text' : json.dumps(response)
        # })
        
        
        
    async def websocket_disconnect(self, event):
        print('disconnect' , event)
        
    async def chat_message(self,event):
        print('chat_message' , event)
        await self.send({
            'type' : 'websocket.send',
            'text' : event['text']
        })
    
    
    
    @database_sync_to_async
    def get_user_object(self , user_id):
        
        
        qs = User.objects.filter(id=user_id)
    
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        # print(obj , 'userrrrrrrrrrrrrrrrrrrrrrrr')
        return obj
        
    @database_sync_to_async
    def get_game_object(self , game_id):
        qs = Game.objects.filter(id = game_id)
        if qs.exists() :
            obj = qs.first()
        else :
            obj = None
            
        # print(obj , "gameeeeeeeeeeeeeeeeeeeeeeeeee")
        return obj
    
    @sync_to_async
    def create_message(self, send_by_id, send_to_id, msg):
        try:
            user = User.objects.get(id=send_by_id)
            game = Game.objects.get(id=send_to_id)
            message = Message(user=user, game=game, message=msg)
            message.save()
            return message
        except Exception as e:
            # Handle exceptions or errors here
            print(f"Error creating message: {e}")
            return None