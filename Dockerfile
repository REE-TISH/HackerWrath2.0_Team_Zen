# Use an official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files & enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY . .

# Expose port for Gunicorn/Django
EXPOSE 8000

# Run server using Gunicorn
CMD ["gunicorn", "Sov_Backend.wsgi:application", "--bind", "0.0.0.0:8000"]
