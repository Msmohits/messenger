import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()
channel.queue_declare(queue='result')
# channel.exchange_declare(exchange='exchange1', exchange_type='direct')
def receiver(ch, method, properties, body):
    # channel.queue_bind(exchange='exchange1', queue='hi', routing_key='key1')
    # method_frame, header_frame, body = channel.basic_get(queue='hi', auto_ack=True)
    if body:
        print('id: ',properties.message_id, 'message:',body.decode())
        channel.basic_publish(exchange='', routing_key='input', body=body,
                              properties=pika.BasicProperties(message_id=properties.message_id))


channel.basic_consume(queue='input', on_message_callback=receiver, auto_ack=True)
print('Waiting for messages. To exit press CTRL+C')


channel.start_consuming()
