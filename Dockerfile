# Use the official Python image as the base image
FROM python:3.10-slim-buster
# Set the working directory in the container to /app
WORKDIR /app
# Copy the requirements.txt file into the container to /app
COPY . /app
# Upgrade pip
RUN pip install --upgrade pip
# Install any other packages
RUN pip install --no-cache-dir -r requirements.txt
# Set default command to run the Flask application
CMD ["python", "app.py"]