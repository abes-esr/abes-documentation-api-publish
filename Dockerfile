FROM python:3.11-slim
ARG DOCUMENTATION_API_PUBLISH_SCENARI_API_FOLDER

WORKDIR /app

COPY . .
COPY requirements.txt requirements.txt
COPY config-module/config/${DOCUMENTATION_API_PUBLISH_SCENARI_API_FOLDER}/* config/
COPY config-module/config/items_to_purge.json config/items_to_purge.json
COPY config-module/config/generator_types_codes.json config/generator_types_codes.json
RUN mkdir -p tmp

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install config-module/lib/scenaripy_api-6.4.0.tar.gz
RUN pip install config-module/lib/${DOCUMENTATION_API_PUBLISH_SCENARI_API_FOLDER}/SCENARIchain-server_final_python.tar.gz

EXPOSE 8000:8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]