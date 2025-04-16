FROM python:3.11-slim

WORKDIR /app

COPY . .
COPY requirements.txt requirements.txt
RUN mkdir -p ../tmp

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install lib/scenaripy_api-6.4.0.tar.gz
RUN pip install lib/${GENERATION_SCENARI_API_FOLDER}/SCENARIchain-server_6.3.13final_python.tar.gz

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]