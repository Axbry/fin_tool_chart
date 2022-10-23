import asyncio
import datetime
import json
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from random import random

from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from fastapi_utils.tasks import repeat_every
from dateutil import relativedelta
from redistimeseries.client import Client 

rts = Client(host='redislocal', port=6379)

origins = [
    "http://localhost:8081",
    "http://localhost:8080",
]

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def format_timestamp(timestamp: int) -> str:
    return datetime.datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S") 

# todo: remove
@app.get('/test_stream/{queue}')
async def test_stream(queue: str, request: Request):
    async def event_generator():
        counter = 0
        while True:
            yield {
                "event": "message",
                # todo: generate id
                "id": "message_id",
                "retry": 500,
                "data": json.dumps({
                    'counter': counter,
                    'queue': queue
                })
            }
            counter += 1
            await asyncio.sleep(2) 
    return EventSourceResponse(event_generator())

@app.get('/stream_data/{ticker}/{time_frame}/{last_time_stamp}')
async def message_stream(ticker: str, time_frame: str, last_time_stamp: int, request: Request):
    from_time = last_time_stamp
    async def event_generator():
        nonlocal from_time
        while True:
            # If client was closed the connection
            if await request.is_disconnected():
                print('disconnected')
                break
            to_time = int(datetime.datetime.now().timestamp()) * 1000
            points = rts.range(f'{ticker}:{time_frame}', 
                from_time = from_time, 
                to_time   = to_time)

            for p in points:
                print(f'point {p} yielded')
                yield {
                    "event": "message",
                    # todo: generate id
                    "id": "message_id",
                    "retry": 500,
                    "data": json.dumps({
                        'label': format_timestamp(p[0]),
                        'data': p[1]
                    })
                }
            if points:
                from_time = to_time

            await asyncio.sleep(1)
    print('response is about to be sent')
    return EventSourceResponse(event_generator())


@app.get('/fin_tools')
async def get_fin_tools():
    return [
        {
            'text': f'ticker_{i:02d}',
            'value': f'ticker_{i:02d}'
        }
        for i in range(100)
    ]


@app.get("/price/{ticker}/{time_frame}")
async def get_price(ticker: str, time_frame: str):
    global last_time_stamp
    print(rts)

    from_time = int(datetime.datetime(2022, 1, 1).timestamp()) * 1000
    points = rts.range(
        f'{ticker}:{time_frame}', 
        from_time = from_time, 
        to_time = int(datetime.datetime.now().timestamp()) * 1000)
    
    chart_data = {
        'labels': [format_timestamp(p[0]) for p in points],
        'datasets': [
            {
                'label': str(ticker),
                'backgroundColor': '#f87979',
                'data': [p[1] for p in points]
            }
        ]
    }

    last_time_stamp = max([p[0] for p in points], default=from_time)
    extra_data = {'ticker': ticker, 'last_time_stamp': last_time_stamp }
    return {'chart_data': chart_data, 'extra_data': extra_data}
