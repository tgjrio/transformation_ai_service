# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary dependencies specified in requirements.txt
# (If you have a requirements.txt file)
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable (optional if you have environment variables to set)
ENV PYTHONUNBUFFERED=1

# Run the application
# Replace `app.py` with the name of your main script
CMD ["python", "main.py"]