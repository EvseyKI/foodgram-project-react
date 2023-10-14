FROM python:3.10.9-slim
SHELL ["/bin/bash", "-c"]
RUN pip install --upgrade pip
RUN pip install gunicorn
WORKDIR /food
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod +x manage.py
CMD ["gunicorn","-b","0.0.0.0:8080","foodgram.wsgi"]
