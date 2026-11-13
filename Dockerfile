# LeakTrace decoder API (Render free web service, or any Docker host).
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin \
      libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libharfbuzz-subset0 \
      fonts-liberation fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
COPY --chown=user . .

ENV PYTHONPATH=/home/user/app LEAKTRACE_DATA=/tmp/leaktrace LEAKTRACE_ORIGINS=https://abijith-kumar-sinha.github.io
EXPOSE 7860
# Render injects $PORT; elsewhere it defaults to 7860.
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-7860}
