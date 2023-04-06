# from core2 import send_message, setup_rabbitmq
import json

import aio_pika
from fastapi import Response

async def setup_rabbitmq():
    connection = await aio_pika.connect_robust(host='localhost')

    channel = await connection.channel()
    queue1 = await channel.declare_queue('queue3')
    queue2 = await channel.declare_queue('queue4')

    return connection, channel, queue1, queue2


async def re_send(channel, queue2, message):

    message_body = eval(message.body.decode())
    # print('jjjjjjj',message_body, type(message_body))
    modified_message = f'{message_body["message"]} world, id: {message_body["id"]}'

    # print(f'Received message: {message_body}, Modified message: {modified_message}')
    return modified_message

async def receive():
    connection, channel, queue1, queue2 = await setup_rabbitmq()

    async with queue1.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print(message.body)
                await re_send(channel, queue2, message)
                return Response(content=message, media_type='text/plain')