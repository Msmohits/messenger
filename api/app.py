import json
import os
import uvicorn
from aio_pika import Message, connect
from fastapi import FastAPI
import asyncio
import uuid

app = FastAPI()

response_data = {}

@app.post('/send')
async def send(request: dict):
    print(os.getenv('test'))
    connection = await connect(os.getenv('test'))
    message_id = uuid.uuid4()
    print(message_id)
    request['message_id'] = str(message_id)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("hello")
        message = json.dumps(request).encode()
        await channel.default_exchange.publish(
            Message(message),
            routing_key=queue.name,
        )

        print("Sent:", request)
        queue1 = await channel.declare_queue("hell2", durable=True)
        async with queue1.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    message = json.loads(message.body)
                    response_data.update(message)
                    if str(message_id) == str(message.get('message_id')):
                        return response_data

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    uvicorn.run("app:app", host=os.getenv('test'), port=6001)
