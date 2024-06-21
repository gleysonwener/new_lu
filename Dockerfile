FROM python:3.11.4-slim

# 
WORKDIR /code

#
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY . /code/

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]



