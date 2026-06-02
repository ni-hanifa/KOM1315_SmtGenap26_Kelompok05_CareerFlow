# backend/Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend code
COPY . .

# Expose port 5001 for the Flask app
EXPOSE 5001

# Run the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]