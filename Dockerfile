FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG BUILD_SHA=dev
ENV BUILD_SHA=$BUILD_SHA

EXPOSE 8000

CMD ["uvicorn", "platform_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
