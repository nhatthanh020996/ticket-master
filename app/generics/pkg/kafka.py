import logging
import json
import sys
import uuid
from typing import Callable, List
import traceback

from confluent_kafka import Consumer, TopicPartition, OFFSET_STORED, OFFSET_BEGINNING
from confluent_kafka.deserializing_consumer import DeserializingConsumer
from confluent_kafka.serializing_producer import SerializingProducer
from confluent_kafka import KafkaError
from confluent_kafka import KafkaException

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HandlingMessageBaseCallback:
    enable_check_auth = False
    message_model: BaseModel = None

    def __init__(self, message):
        self.message_value_dict = message.value()
        self.key = message.key()
        self.topic = message.topic()
        self.partition = message.partition()
        self.offset = message.offset()
        self._error = None
    
    def __enter__(self):
        pass

    def __exit__(self):
        pass
    
    def execute(self):
        try:
            self.initialize()
            self.validate(self.message_value_dict)
            response = self.handle_message()
            extra = {'topic': self.topic, 'partition': self.partition, 'offset': self.offset, 'key': self.key}
            logger.info('Message was handled sucessfully!', extra=extra)
        except Exception as exc:
            response = None
            self.handle_exception(exc)
        self.finalize(response)

    def validate(self, message):
        assert issubclass(self.message_model, BaseModel), (
            '`message_model` is required.'
        )
        self.message = self.message_model.model_validate(message)

    def authenticate(self):
        pass

    def initialize(self, **kwargs):
        if self.enable_check_auth:
            self.authenticate()
        return None

    def handle_message(self):
        raise NotImplementedError(
            'subclasses of AMQPConsumeBaseCommand must provide a handle_message() method'
        )

    def handle_exception(self, exc):
        """
        """
        self._error = traceback.format_exc()
        extra = {'topic': self.topic, 'partition': self.partition, 'offset': self.offset, 'key': self.key}
        logger.exception('An Exception Occurs', extra=extra)
        self.send_notification()
    
    def send_notification(self):
        pass

    def finalize(self, response, *args, **kwargs):
        """
        """
        pass

    @property
    def error(self):
        return self._error

def UUIDKeyDeserializer(key, ctx):
    if key is None:
        return key
    return uuid.UUID(key.decode('utf-8'))

def JSONValueDeserialize(value, ctx):
    return json.loads(value)


class KafkaBaseConsumer:
    callback = HandlingMessageBaseCallback
    consumer_config = None
    topics = None
    max_time_retry = 1
    
    def __init__(self):
        self.set_consumer()

    def set_consumer(
        self,
        key_deserializer: Callable = UUIDKeyDeserializer,
        value_deserializer: Callable = JSONValueDeserialize
    ):
        self.consumer_config['enable.auto.commit'] = False
        self.consumer_config['key.deserializer'] = key_deserializer
        self.consumer_config['value.deserializer'] = value_deserializer
        self.consumer = DeserializingConsumer(self.consumer_config)

    def process_message(self, message):
        """
        """
        num_time_exec = 0
        while num_time_exec < self.max_time_retry:
            callback = self.callback(message)
            callback.execute()
            if callback.error is None:
                self.consumer.commit()
                break
            num_time_exec = num_time_exec + 1

    def start_consume(self):
        print('Start to consume message at topic: {}'.format(self.topics))
        while True:
            try:
                self.consumer.subscribe(self.topics)
                while True:
                    msg = self.consumer.poll(timeout=1.0)
                    if msg is None: continue
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                            (msg.topic(), msg.partition(), msg.offset()))
                        elif msg.error():
                            raise KafkaException(msg.error())
                    
                    # Consumer just move on the next message when the current message is handled successfully!
                    logger.info('Incomming Message', extra={'topic': msg.topic(), 'partition': msg.partition(), 'offset': msg.offset(), 'key': msg.key()})
                    self.process_message(msg)

            except KeyboardInterrupt:
                print('XXXX: KeyboardInterrupt')
                break
            except KafkaException:
                logger.exception('Kafka Error Occurs')
            except Exception:
                logger.exception('Unexpected Exception Occurs')    
                break
        self.consumer.close()
    
    def consume_single_message(self, partition: int, offset: int):
        print("topic: {}".format(self.topics[0]))
        tp = TopicPartition(self.topics[0], partition, offset)
        self.consumer.assign([tp])
        self.consumer.seek(tp)
        msg = self.consumer.poll(timeout=1.0)
        if msg is not None:
            if not msg.error():
                logger.info('Incomming Message', extra={'topic': msg.topic(), 'partition': msg.partition(), 'offset': msg.offset(), 'key': msg.key()})
                self.process_message(msg)
            
            else:
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print("Reached end of partition")
                else:
                    print(f"Error: {msg.error()}")
        else:
            print("No message received")
        self.consumer.close()
    
    def consume_range_message(self, partition: int, start_offset: int, end_offset):
        print(
            "topic: {}, consume messsage in partition {} from offset {} to offset {}".
            format(self.topics[0], partition, start_offset, end_offset)
        )
        tp = TopicPartition(self.topics[0], partition, start_offset)
        self.consumer.assign([tp])
        self.consumer.seek(tp)
        while True:
            try:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None: break
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print('%% %s [%d] reached end at offset %d\n' % (msg.topic(), msg.partition(), msg.offset()))
                    else:
                        print(msg.error())
                    break

                if msg.offset() > end_offset:
                    print(f"Reached specified end offset {end_offset}")
                    break
                logger.info('Incomming Message', extra={'topic': msg.topic(), 'partition': msg.partition(), 'offset': msg.offset(), 'key': msg.key()})
                self.process_message(msg)
            except KeyboardInterrupt:
                print('XXXX: KeyboardInterrupt')
                break
            except KafkaException:
                logger.exception('Kafka Error Occurs')
            except Exception:
                logger.exception('Unexpected Exception Occurs')
            self.consumer.close()

class KafkaProducer:
    def __init__(self, config: dict):
        self.config = config
        self.producer = SerializingProducer(config)

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error('Delivery message failed', extra={'key': msg.key()})
        else:
            logger.info('Delivery message successfully!', extra={
                'topic': msg.topic(), 'partition': msg.partition()
            })

    def produce(self, topic: str, key, value: dict, partition: int=None):
        """
        """
        if partition is None:
            if key is not None:
                self.producer.produce(topic, key, value, on_delivery=self.delivery_report)
            else:
                self.producer.produce(topic, value=value, on_delivery=self.delivery_report)
        else:
            if key is not None:
                self.producer.produce(topic, key, value, partition, on_delivery=self.on_delivery)
            else:
                self.producer.produce(topic, value=value, partition=partition, on_delivery=self.on_delivery)
        self.producer.flush()


def UUIDKeySerializer(key: uuid.UUID, ctx):
    return str(key).encode('utf-8')

def JSONValueSerialize(value: dict, ctx):
    return json.dumps(value)
