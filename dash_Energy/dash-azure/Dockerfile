# Base Image
FROM python:3

# Install Python and pip
RUN mkdir /app
WORKDIR /app

# Copy files required for the app to run
ADD requirements.txt /app/
RUN pip install --upgrade cython
RUN pip install --upgrade pip

# Install required files
RUN pip install -r requirements.txt
ADD . /app/

# Run the application
CMD ["python", "application.py"]