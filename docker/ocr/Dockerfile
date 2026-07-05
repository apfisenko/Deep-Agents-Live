FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY docker/ocr/requirements-ocr.txt /tmp/requirements-ocr.txt
RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r /tmp/requirements-ocr.txt

ENV PYTHONPATH=/work/backend:/work/evals/scripts
ENV EASYOCR_MODULE_PATH=/root/.EasyOCR

COPY docker/ocr/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
