# basic python image
FROM python:3.10-alpine

# todo: copy src
COPY . ./
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED=1

WORKDIR ./src
# start command
CMD [ "python", "./main.py" ]
