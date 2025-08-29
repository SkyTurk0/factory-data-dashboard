# backend/Dockerfile
FROM python:3.12-slim

# Install system deps + unixODBC + Microsoft ODBC Driver 18
# (Needed for pyodbc to import and talk to SQL Server)
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl gnupg2 apt-transport-https \
      build-essential unixodbc unixodbc-dev \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
         | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
         > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# System deps (add msodbcsql18 if you later run backend INSIDE container with pyodbc; for now host ODBC is fine)
WORKDIR /app

# Install Python deps
COPY /requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY /backend .

# Dev-friendly defaults
ENV FLASK_ENV=development
EXPOSE 5000

# Run with debug reloader and 0.0.0.0 binding
CMD ["flask", "--app", "app.py", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
