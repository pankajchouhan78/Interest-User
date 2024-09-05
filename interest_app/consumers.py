# import json
# from asgiref.sync import async_to_sync
# from channels.generic.websocket import WebsocketConsumer
# from django.contrib.auth import get_user_model
# from interest_app.models import ChatMessage
# from asgiref.sync import database_sync_to_async

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         print("Connecting: ", self)
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, self.channel_name
#         )
#         self.accept()

#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )

#     # Receive message from WebSocket
#     def receive(self, text_data):
#         test_data_json = json.loads(text_data)
#         message = test_data_json["message"]

#         user = self.scope["user"]
#         username = user.username if user.is_authenticated else "Anonymous"

#         # Send message to room group with sender information
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {"type": "chat.message", "message": message, "sender": username},
#         )


#     # def receive(self, text_data):
#     #     import pdb; pdb.set_trace()
#     #     text_data_json = json.loads(text_data)
#     #     message = text_data_json["message"]

#     #     user = self.scope["user"]
#     #     username = user.username if user.is_authenticated else "Anonymous"

#     #     # Determine receiver based on your application logic
#     #     # Here, I'm using a dummy receiver; replace it with actual logic
#     #     receiver_username = "receiver_username"  # Example placeholder; replace with actual logic
#     #     User = get_user_model()
#     #     receiver = User.objects.get(username=receiver_username)

#     #     # Save message to the database
#     #     if user.is_authenticated:
#     #         ChatMessage.objects.create(
#     #             sender=user,
#     #             receiver=receiver,
#     #             message=message
#     #         )

#     #     # Send message to room group with sender information
#     #     async_to_sync(self.channel_layer.group_send)(
#     #         self.room_group_name,
#     #         {
#     #             "type": "chat.message",
#     #             "message": message,
#     #             "sender": username,
#     #         }
#     #     )


#     # Receive message from room group
#     def chat_message(self, event):

#         message = event["message"]
#         sender = event["sender"]

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": message, "sender": sender}))


# ----------------------------------------------------------------


# import json
# import logging
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth import get_user_model
# from interest_app.models import ChatMessage

# User = get_user_model()
# logger = logging.getLogger(__name__)

# # import django

# # django.setup()  # Ensure Django settings are set up

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # logger.debug("Attempting to connect WebSocket")
#         self.user = self.scope["user"]
#         if not self.user.is_authenticated:
#             logger.debug("User not authenticated, closing WebSocket")
#             await self.close()
#             return
#         self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]
#         self.other_user = await self.get_user(self.other_user_id)
#         if not self.other_user:
#             logger.debug("Other user not found, closing WebSocket")
#             await self.close()
#             return
#         self.room_group_name = f"chat_{min(self.user.id, self.other_user.id)}_{max(self.user.id, self.other_user.id)}"
#         logger.debug(f"User {self.user.id} connected to room {self.room_group_name}")
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()
#         logger.debug("WebSocket connection accepted")

#     async def disconnect(self, close_code):
#         logger.debug(f"WebSocket disconnected with code {close_code}")
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         logger.debug(f"Message received: {text_data}")
#         if not text_data:
#             logger.debug("No data received, closing WebSocket")
#             await self.close()
#             return
#         try:
#             text_data_json = json.loads(text_data)
#         except json.JSONDecodeError:
#             logger.error("Invalid JSON received")
#             await self.close()
#             return
#         message = text_data_json.get("message")
#         if not message:
#             logger.debug("No message found in JSON, closing WebSocket")
#             await self.close()
#             return
#         await self.save_message(message)
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {"type": "chat_message", "message": message, "sender": self.user.username},
#         )

#     async def chat_message(self, event):
#         message = event["message"]
#         sender = event["sender"]
#         logger.debug(f"Sending message: {message} from {sender}")
#         await self.send(text_data=json.dumps({"message": message, "sender": sender}))

#     @database_sync_to_async
#     def get_user(self, user_id):
#         try:
#             return User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             logger.error(f"User with ID {user_id} does not exist")
#             return None

#     @database_sync_to_async
#     def save_message(self, message):
#         ChatMessage.objects.create(
#             sender=self.user, receiver=self.other_user, message=message
#         )


# **************************************************************** update code with no logger

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from interest_app.models import ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.other_user = await self.get_user(self.other_user_id)
        if not self.other_user:
            await self.close()
            return
        self.room_group_name = f"chat_{min(self.user.id, self.other_user.id)}_{max(self.user.id, self.other_user.id)}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        if not text_data:
            await self.close()
            return
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            await self.close()
            return
        message = text_data_json.get("message")
        if not message:
            await self.close()
            return
        await self.save_message(message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": message, "sender": self.user.username},
        )

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        await self.send(text_data=json.dumps({"message": message, "sender": sender}))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, message):
        ChatMessage.objects.create(
            sender=self.user, receiver=self.other_user, message=message
        )
