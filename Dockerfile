# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit dashboard file into the container
# This is crucial for the dashboard service
COPY streamlit/dashboard.py /data/dashboard.py

# Expose the port that Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app
# This command is overwritten by docker-compose, but it's good practice
CMD ["streamlit", "run", "/data/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]