# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install the project's dependencies from requirements.txt
COPY ../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install
RUN playwright install-deps

# Copy the rest of your application's code
COPY ../../ .

# Expose the port the app runs on
EXPOSE 8000

# Run the command to start uWSGI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
