# Base pinned by tag python:3.10-slim (same major.minor as the original image
# built 2025-09-23). The exact base digest used on 2025-09-23 is NOT measurable
# from a built image (docker history keeps no base RepoDigest) — using a guessed
# digest would be wrong, so the tag plus the locked requirements below it.
FROM python:3.10-slim

WORKDIR /app

# Copy required files into the container
COPY ./requirements.txt ./requirements-locked.txt /app/
COPY ./VERSION /app

# REQ-270/TH-661 bước 3b (PO #44713): ĐÓNG BĂNG THƯ VIỆN theo image gốc 23-09
# (pip freeze trong ghcr.io/snailyp/gemini-balance@1508249) — build từ tip hôm nay
# kéo thư viện mới gây 500 jinja; lock giữ đúng bộ version image đang chạy.
RUN pip install --no-cache-dir -r requirements-locked.txt
COPY ./app /app/app
ENV API_KEYS='["your_api_key_1"]'
ENV ALLOWED_TOKENS='["your_token_1"]'
ENV TZ='Asia/Shanghai'

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
