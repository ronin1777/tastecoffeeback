# Use the official Python image as a base image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files
# and to ensure that Python outputs logs directly to the terminal.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the entire Django project into the container
COPY . .

# Collect static files (if applicable)
# RUN python manage.py collectstatic --noinput

# Make migrations (optional, you may skip this if you manage migrations elsewhere)
RUN python manage.py migrate

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tastecofee.wsgi:application"]
