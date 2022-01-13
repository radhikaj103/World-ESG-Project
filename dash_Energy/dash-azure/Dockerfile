FROM python:3

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip install --upgrade cython
RUN pip install --upgrade pip

RUN pip install -r requirements.txt
ADD . /app/

ENTRYPOINT [ "python" ]
CMD ["application.py"]