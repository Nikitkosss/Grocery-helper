FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . ./

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]