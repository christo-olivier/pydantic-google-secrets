FROM python:3.11.5-slim

WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install --upgrade pip

COPY ./requirements.txt .
COPY ./pydantic_google_secrets/* .

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python", "app.py" ]