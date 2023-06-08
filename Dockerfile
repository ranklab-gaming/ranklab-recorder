# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD worker.py requirements.txt ui bin/start /app/

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install host deps
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
      openssh-client \
      xvfb \
      freerdp2-x11 \
      curl \
      unzip \
      sshpass \
    && rm -rf /var/lib/apt/lists/*

# Install the AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf awscliv2.zip aws

# Run app.py when the container launches
CMD ["./bin/start"]
