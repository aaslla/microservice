FROM python:alpine3.6

COPY application.py /
RUN pip install flask

ENTRYPOINT ["python"]
CMD ["-u", "application.py"]