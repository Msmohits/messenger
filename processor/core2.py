# import asyncio
import json

import aio_pika
import uvicorn
from fastapi import FastAPI, Response
from core1 import re_send

app = FastAPI()

async def setup_rabbitmq():
    connection = await aio_pika.connect_robust(host='localhost')

    channel = await connection.channel()
    queue1 = await channel.declare_queue('queue3')
    queue2 = await channel.declare_queue('queue4')

    return connection, channel, queue1, queue2


async def send_message(channel, queue, message):
    await channel.default_exchange.publish(
        aio_pika.Message(body=message.encode()),
        routing_key=queue.name
    )
    # print(f'Sent message: {message}')


@app.post('/send')
async def send(request: dict, queue1 = None):
    # print(request, json.dumps(request).encode('utf-8'))
    if not queue1:
        connection, channel, queue1, queue2 = await setup_rabbitmq()

    await send_message(channel, queue1, json.dumps(request))
    return {'message': 'Sent message successfully'}


@app.get('/receive2')
async def receive2():
    connection, channel, queue1, queue2 = await setup_rabbitmq()
    async with queue1.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                # print(message.body)
                message = await re_send(channel, queue2, message)
                await send_message(channel, queue2, message)

            async with queue2.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        # print(message.body)
                        # print(message.message_id)
                        return Response(content=message.body, media_type='text/plain')


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)

