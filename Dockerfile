# Use the official Python image with Alpine as the base image
FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the files into the container
COPY requirements.txt .
COPY app.py .
COPY model.py .

# Create and activate a virtual environment (is it really necessary?)
#RUN python -m venv venv
#RUN source venv/bin/activate

# Install any dependencies
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5002

# Specify the command to run on container start
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5002", "app:app"]

