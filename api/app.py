import json
import os
import uvicorn
from aio_pika import Message, connect
from fastapi import FastAPI
import asyncio
import uuid

app = FastAPI()


response_data = {}

async def receive():
    connection = await connect(os.getenv('test'))
    channel = await connection.channel()
    queue1 = await channel.declare_queue("hell2", durable=True)
    # # await queue1.purge()
    async with queue1.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                response_data.update(json.loads(message.body))
                # print('RRRRRRRRR', response_data)

                return response_data


@app.post('/send')
async def send(request: dict):
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

        try:
            for i in range(10):
                response = await receive()
                if str(message_id) == str(response['message_id']):
                    return response
        except TimeoutError:
            print("Response not found, timeout")


if __name__ == "__main__":
    # asyncio.run(receive())
    uvicorn.run("app:app", host=os.getenv('test'), port=8001)