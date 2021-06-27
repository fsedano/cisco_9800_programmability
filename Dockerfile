FROM python:3.8
RUN pip install --upgrade pip
WORKDIR /app
COPY app/requirements.txt /app/
RUN pip install -r requirements.txt
COPY /app/ /app/
ENTRYPOINT [ "/bin/bash", "-c", "sleep 9999999" ]
