FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./requirements.txt
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
# Whitelisted source copies: never copy .env, user files, git or policy caches.
COPY --chmod=0644 profile_backup.py benefit_journeys.py app_context.py ./
COPY --chmod=0644 backend/__init__.py backend/api.py backend/models.py ./backend/
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "backend.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
