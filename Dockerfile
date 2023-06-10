# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install host deps
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
      xvfb \
      freerdp2-x11 \
      curl \
      unzip \
      scrot \
      libcurl4-openssl-dev \
      python3-tk \
      python3-dev \
      libssl-dev \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install the AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf awscliv2.zip aws

# Start the worker
CMD ["./bin/start"]
