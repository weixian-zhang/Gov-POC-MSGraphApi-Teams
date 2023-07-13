# Use the official Python 3.10 image as the base image
FROM python:3.10.0-alpine as builder

# Set the working directory inside the container
WORKDIR /app

# Install build dependencies
RUN apk --no-cache add build-base
# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy the rest of the application files to the container
COPY . .

from python:3.10.0-alpine

WORKDIR /app

# contains python modules
COPY --from=builder /root/.local /root/.local

COPY --from=builder /app /app

EXPOSE 5000

# Set the command to run the application
CMD ["python", "main.py"]