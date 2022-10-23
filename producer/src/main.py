import pickle
from collections import defaultdict
from datetime import datetime
import asyncio

import pika
import os

from models import FinToolMovement
from settings import *
from random import random

url_params = pika.URLParameters(RABBITMQ_URL)
connection = pika.BlockingConnection(url_params)
channel = connection.channel()
queue = channel.queue_declare(QUEUE_NAME, durable=True)

prices = defaultdict(int)

def generate_movement():
    movement = -1 if random() < 0.5 else 1
    return movement


async def notify_movement(ticker: str) -> None:
    movement_time = datetime.now()
    movement = generate_movement()
    prices[ticker] += movement
    fin_tool_movement = FinToolMovement(ticker=ticker, timestamp=movement_time, movement=movement, price=prices[ticker])
    serialised_movement = fin_tool_movement.to_json()
    channel.basic_publish(exchange='',
                          routing_key=QUEUE_NAME,
                          properties=pika.BasicProperties(
                              delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                          ),
                          body=serialised_movement)
    await asyncio.sleep(1)


async def main():
    while True:
        tasks = list()
        for i in range(FIN_TOOLS_COUNT):
            ticker = f'ticker_{i:02d}'
            task = asyncio.create_task(notify_movement(ticker))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        connection.close()
