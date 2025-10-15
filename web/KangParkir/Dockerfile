# Use the official Python 3.11 image as the base image
FROM python:3.10.12

# Set the working directory inside the container
WORKDIR /app

# Copy the entire app directory into the container at /app
COPY . .

# Install the required Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Specify the entry point command to run your app.py file
CMD ["python3", "app.py"]
