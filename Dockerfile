FROM python:3.4.3
ENV HOME /lope.anno
WORKDIR $HOME
ADD . $HOME
RUN pip install -r pip.txt uwsgi
CMD ["uwsgi", "--uid", "root", "--master", "--http", "0.0.0.0:8001", "--module", "core.wsgi", "--static-map", "/static_lopeanno=static",  "--process", "2"]

