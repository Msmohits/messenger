import asyncio
import json
import os

from aio_pika import connect, Message
from aio_pika.abc import AbstractIncomingMessage

async def on_message(message: AbstractIncomingMessage) -> None:
    connection = await connect(os.getenv('test'))
    async with connection:
        channel = await connection.channel()
        queue1 = await channel.declare_queue("hell2", durable=True)

        message = json.loads(message.body)
        message["message"] = f'{message["message"]} world'

        await channel.default_exchange.publish(
            Message(json.dumps(message).encode()),
            routing_key=queue1.name,
        )
    print('ppp',message)
    return message

async def receive() -> None:
    connection = await connect(os.getenv('test'))
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("hello")

        while True:
            event = asyncio.Event()
            await queue.consume(on_message)
            await event.wait()




while True:
    try:
        asyncio.run(receive())
    except KeyboardInterrupt:
        break