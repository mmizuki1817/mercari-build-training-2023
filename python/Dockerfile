# docker image build -t build2023/app:latest -f python/Dockerfile .
# docker run -d -p 9000:9000 build2023/app:latest

FROM python:3.10.6-alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari

WORKDIR /app

COPY python python 
COPY db db

COPY /python/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN mkdir -p /app/db && mkdir -p /app/python/images

RUN chown -R trainee:mercari /app/db
RUN chown -R trainee:mercari /app/python

USER trainee

WORKDIR /app/python
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
