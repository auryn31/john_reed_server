FROM python:rc-alpine3.12

RUN pip install requests
RUN pip install redis
CMD ["python", "-u", "john_reed.py"]