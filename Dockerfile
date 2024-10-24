


FROM hub.hamdocker.ir/library/python:3.11

WORKDIR /tastecofee/
ADD ./requirements.txt ./
RUN pip install --upgrade pip && pip install -r ./requirements.txt

ADD ./ ./
ENTRYPOINT ["/bin/sh", "-c" , "python manage.py makemigrations && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 tastecofee.wsgi"]
