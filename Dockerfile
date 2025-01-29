FROM python:3.11-alpine as base

# build phase
FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --no-cache-dir --prefix=/install -r /requirements.txt

# run phase
FROM base

COPY --from=builder /install /usr/local
COPY app.py model.py /app

EXPOSE 5002

WORKDIR /app
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5002", "app:app"]

