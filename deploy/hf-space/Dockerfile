# LeakTrace decoder API for a Hugging Face Docker Space.
# The Space only needs this file + README.md: the code is cloned from the GitHub fork at build time.
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      git tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin \
      libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libharfbuzz-subset0 \
      fonts-liberation fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
WORKDIR /home/user/app

ARG REPO=https://github.com/Abijith-Kumar-Sinha/Leaktrace.git
ARG REF=main
RUN git clone --depth 1 --branch $REF $REPO . && pip install --no-cache-dir --user -r requirements.txt

ENV PYTHONPATH=/home/user/app LEAKTRACE_DATA=/tmp/leaktrace
EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
