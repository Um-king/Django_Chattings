# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import async_to_sync

# class ChatConsumer(AsyncWebsocketConsumer):
# 	async def connect(self):
# 		self.room_name = self.scope['url_route']['kwargs']['room_name']
# 		self.room_group_name = 'chat_%s' % self.room_name

# 		await self.channel_layer.group_add(
# 			self.room_group_name,
# 			self.channel_name
# 		)

# 		await self.accept()

# 	async def disconnect(self, close_code):
# 		await self.channel_layer.group_discard(
# 			self.room_group_name,
# 			self.channel_name
# 		)

# 	async def receive(self, text_data):
# 		text_data_json = json.loads(text_data)
# 		message = text_data_json['message']

# 		await self.channel_layer.group_send(
# 			self.room_group_name,
# 			{
# 				'type': 'chat_message',
# 				'message': message
# 			})

# 	async def chat_message(self, event):
# 		message = event['message']

# 		await self.send(text_data=json.dumps({
# 			'message': message
# 		}))



# video 추가
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = 'chat_%s' % self.room_name

		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)

		await self.accept()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)

	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		# 메시지가 신호 데이터인지 확인
		if 'signal' in text_data_json:
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'video_signal',
					'signal': text_data_json['signal']
				}
			)
		else:
			message = text_data_json['message']

			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'chat_message',
					'message': message
				})

	async def chat_message(self, event):
		message = event['message']

		await self.send(text_data=json.dumps({
			'message': message
		}))

	# 비디오 신호 처리
	async def video_signal(self, event):
		signal = event['signal']
		await self.send(text_data=json.dumps({
			'signal': signal
		}))