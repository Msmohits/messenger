import json
import os
import uvicorn
from aio_pika import Message, connect
from fastapi import FastAPI

app = FastAPI()

@app.post('/send')
async def send(request: dict):
    connection = await connect(os.getenv('test'))

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("hello")
        message = json.dumps(request).encode()
        await channel.default_exchange.publish(
            Message(message),
            routing_key=queue.name,
        )

        print(" [x] Sent 'Hello World!'")

        queue1 = await channel.declare_queue("hell2", durable=True)
        await queue1.purge()
        async with queue1.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print('mmmm', message.body)

                    return json.loads(message.body)


if __name__ == "__main__":
    uvicorn.run(host=os.getenv('test'), port=8001)
