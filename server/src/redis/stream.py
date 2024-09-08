from .config import Redis

class StreamConsumer:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        print(f"StreamConsumer initialized with redis_client: {redis_client}")

    async def consume_stream(self, block: int,  stream_channel):
        response = await self.redis_client.xread(
            streams={stream_channel:  '0-0'}, block=block)
        print(f"Stream response: {response}")
        return response

    async def print_all_messages(self, stream_channel):
        messages = await self.redis_client.xrange(stream_channel, min='0', max='+')
        print(f"Messages in stream {stream_channel}:")
        for msg in messages:
            print(f"Message ID: {msg[0]}, Data: {msg[1]}")

    async def delete_message(self, stream_channel, message_id):
        await self.redis_client.xdel(stream_channel, message_id)

    async def reset_stream(self, stream_channel):
        while True:
            response = await self.redis_client.xread(streams={stream_channel: '0-0'}, count=100)
            if not response:
                break  # No more messages in the stream
            for stream, messages in response:
                for message in messages:
                    message_id = message[0].decode('utf-8')
                    await self.redis_client.xdel(stream_channel, message_id)
        print(f"Stream '{stream_channel}' has been reset.")
