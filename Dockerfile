# BASE IMAGE
FROM python:3.12-slim

# WORKDIR AND DEPENDENCIES
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

# EXECUTABLE
RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "/app/entrypoint.sh" ]