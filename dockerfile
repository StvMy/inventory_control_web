# Use an official Python runtime as a parent image
FROM python:3.13.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"] 

#python_file_name:flask_name (__name__)
#the CMD file looks like this due to use of gunicorn

# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"] 
# in gunicorn the "--bind", "0.0.0.0:5000" are required 0.0.0.0 tells docker to hear from any port
# the 5000 are the port that will be exposed either in cmd or here so exposing the port 5000 now
# is reccomended