FROM python:3.11-slim
ARG DOCUMENTATION_API_PUBLISH_SCENARI_API_FOLDER

WORKDIR /app

COPY . .
COPY requirements.txt requirements.txt
COPY config/${DOCUMENTATION_API_PUBLISH_SCENARI_API_FOLDER}/* config/
RUN mkdir -p tmp

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install lib/scenaripy_api-6.4.0.tar.gz
RUN pip install lib/${DOCUMENTATION_API_PUBLISH_SCENARI_API_FOLDER}/SCENARIchain-server_6.3.13final_python.tar.gz

EXPOSE 8000:8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]
