FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /project
WORKDIR /project
ADD requirements.txt /project/
RUN pip install -r requirements.txt
ADD testapp /project/
RUN /project/manage.py migrate
CMD ["python3", "/project/manage.py", "runserver", "0.0.0.0:8000"]