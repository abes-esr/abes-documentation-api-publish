FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install scenaripy_api-6.4.0.tar.gz
RUN pip install SCENARIchain-server_6.3.13final_python.tar.gz

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
