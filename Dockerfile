FROM python:3.11-slim
# Install ImageMagick and its development libraries
# These are required for PythonMagick to compile and run
RUN apt-get update && \
    apt-get install -y imagemagick libmagickwand-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app
EXPOSE 80
ENV PYTHONPATH=/app
CMD ["fastapi", "dev", "main.py", "--port", "80", "--host", "0.0.0.0"]
