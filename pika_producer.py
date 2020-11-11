import pika
from pprint import pprint
import json
import uuid

class queue_client():

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='loan-request1', durable=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, data):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='loan-request1',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                delivery_mode=2,  # make message persistent
            ),
            body=f"""{data}""")
        while self.response is None:
            self.connection.process_data_events()
        return self.response


def main():
    data = json.load(open("loan.json"))
    queue_user = queue_client()
    print(' sent loan message: \n', data)
    response = queue_user.call(data)
    print('response: ', response.decode())
    

    """
    with pika.BlockingConnection(pika.ConnectionParameters('localhost')) as connection:
        channel = connection.channel()
        channel.queue_declare(queue='loan-request', durable=True, exclusive=True)
        callback_queue = result.method.queue
        
        channel.basic_publish(exchange='',
                          routing_key='loan-request',
                          body=,
                          properties=pika.BasicProperties(
                            delivery_mode=2,  # make message persistent
                          ))
       """ 
    


if __name__ == "__main__":
    main()
