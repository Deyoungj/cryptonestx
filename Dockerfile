
# Use a lightweight Python image
FROM python:3.12-slim

# Avoid .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
  && apt-get install -y build-essential libpq-dev curl \
  && apt-get clean

# Install Python dependencies
COPY requirements.txt .
# RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir --root-user-action=ignore -r requirements.txt


# Copy project files
COPY . .



COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]


# Expose port
EXPOSE 8004

RUN python manage.py collectstatic --noinput

# Run Gunicorn
CMD ["gunicorn", "cardonecapitalmine.wsgi:application", "--bind", "0.0.0.0:8004"]
