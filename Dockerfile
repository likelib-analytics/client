FROM python:3.7-slim as builder

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip wheel -r requirements.txt -w /wheels

FROM python:3.7-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt --find-links /wheels

COPY . /app


EXPOSE 8080
ENV PYTHONPATH /app

CMD ["python3", "-u", "app.py"]