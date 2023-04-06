import asyncio
from urllib import request

import uvicorn
from fastapi import FastAPI
import aio_pika

app = FastAPI()

# async def main():
    # connection = await aio_pika.connect_robust('localhost')
    # channel= await connection.channel()
    # queue= await channel.declare_queue('input')
    # await sender(queue)

@app.post('/send')
async def send_message(data: dict):
    # Connect to RabbitMQ server
    connection = await aio_pika.connect_robust(host="localhost")
    channel = await connection.channel()

    # Declare a queue to send messages to
    queue_name = "my_queue"
    queue = await channel.declare_queue(queue_name, durable=True)

    # Create a message to send
    message_body = data['message'].encode()
    message = aio_pika.Message(body=message_body, content_type='text/plain', delivery_mode=aio_pika.DeliveryMode.PERSISTENT)

    # Publish the message to the queue
    await channel.default_exchange.publish(message, routing_key=queue_name)

    # Close the connection to RabbitMQ
    await connection.close()

    return {"message": f"Sent '{message}' to {queue_name}"}


@app.get("/receive")
async def receive_message():

    connection = await aio_pika.connect_robust("localhost")
    channel = await connection.channel()

    queue_name = "output"
    queue = await channel.declare_queue(queue_name, durable=True)
    print('qqqqqqqqqqqqqq',queue.iterator())

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                body = message.body.decode()
                return {"message": f"Received '{body}' from {queue_name}"}

    await connection.close()

    return {"message": "No messages in queue"}

if __name__=='__main__':
    uvicorn.run(host='localhost', port=8000)


