import json
import pickle
import sys
from typing import Any

import pika
import pickle
import time
import os
from redistimeseries.client import Client 
from datetime import datetime

from settings import *

rts = Client(host='redislocal', port=6379)


def consume_movement(ch, method, properties, body):
    try:
        fin_tool_movement: dict[str, Any] = json.loads(body)
        ticker = fin_tool_movement.pop('ticker')
        fin_tool_movement.pop('movement')
        rts.add(f'{ticker}:SEC', fin_tool_movement['timestamp'], fin_tool_movement['price'])
    except:
        print(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def create_redis_queue():
    for i in range(100):
        
        ticker = f'ticker_{i:02d}'
        rts.create(f'{ticker}:SEC', labels={ 'TICKER': ticker, 'TIMEFRAME': '1_SEC'})
        rts.create(f'{ticker}:10SEC', labels={ 'TICKER': ticker, 'TIMEFRAME': '10_SEC'})
        rts.createrule(f'{ticker}:SEC', f'{ticker}:10SEC', 'avg', 10000)

        rts.create(f'{ticker}:MIN', labels={ 'TICKER': ticker, 'TIMEFRAME': 'MIN'})
        rts.createrule(f'{ticker}:SEC', f'{ticker}:MIN', 'avg', 60 * 1000)

        rts.create(f'{ticker}:10MIN', labels={ 'TICKER': ticker, 'TIMEFRAME': '10_MIN'})
        rts.createrule(f'{ticker}:SEC', f'{ticker}:10MIN', 'avg', 10 * 60 * 1000)

        rts.create(f'{ticker}:HOUR', labels={ 'TICKER': ticker, 'TIMEFRAME': '1_HOUR'})
        rts.createrule(f'{ticker}:SEC', f'{ticker}:HOUR', 'avg', 60 * 60 * 1000)
        print(f'{ticker} created')


def main():
    create_redis_queue()
    url_params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(url_params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=consume_movement)
    channel.start_consuming()


try:
    # create_redis_queue()
    # timestamp = int(datetime.now().timestamp()) * 1000
    # rts.add('ticker_00', timestamp, 1)
    # print(rts.range('ticker_00', timestamp - 1000, timestamp + 1000))
    main()
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
