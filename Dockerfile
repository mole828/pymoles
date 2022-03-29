FROM python:3.9
COPY / /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
WORKDIR /app
ENTRYPOINT ["python","main.py"]
