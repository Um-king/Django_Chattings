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
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
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


class CallConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        # response to client, that we are connected.
        self.send(text_data=json.dumps({
            'type': 'connection',
            'data': {
                'message': "Connected"
            }
        }))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.my_name,
            self.channel_name
        )

    # Receive message from client WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # print(text_data_json)

        eventType = text_data_json['type']

        if eventType == 'login':
            name = text_data_json['data']['name']

            # we will use this as room name as well
            self.my_name = name

            # Join room
            async_to_sync(self.channel_layer.group_add)(
                self.my_name,
                self.channel_name
            )
        
        if eventType == 'call':
            name = text_data_json['data']['name']
            print(self.my_name, "is calling", name);
            # print(text_data_json)


            # to notify the callee we sent an event to the group name
            # and their's groun name is the name
            async_to_sync(self.channel_layer.group_send)(
                name,
                {
                    'type': 'call_received',
                    'data': {
                        'caller': self.my_name,
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )

        if eventType == 'answer_call':
            # has received call from someone now notify the calling user
            # we can notify to the group with the caller name
            
            caller = text_data_json['data']['caller']
            # print(self.my_name, "is answering", caller, "calls.")

            async_to_sync(self.channel_layer.group_send)(
                caller,
                {
                    'type': 'call_answered',
                    'data': {
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )

        if eventType == 'ICEcandidate':

            user = text_data_json['data']['user']

            async_to_sync(self.channel_layer.group_send)(
                user,
                {
                    'type': 'ICEcandidate',
                    'data': {
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )

    def call_received(self, event):

        # print(event)
        print('Call received by ', self.my_name )
        self.send(text_data=json.dumps({
            'type': 'call_received',
            'data': event['data']
        }))


    def call_answered(self, event):

        # print(event)
        print(self.my_name, "'s call answered")
        self.send(text_data=json.dumps({
            'type': 'call_answered',
            'data': event['data']
        }))


    def ICEcandidate(self, event):
        self.send(text_data=json.dumps({
            'type': 'ICEcandidate',
            'data': event['data']
        }))
