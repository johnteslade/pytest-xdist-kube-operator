FROM python:3.7
RUN pip install kopf && pip install kubernetes
COPY operator_handler.py /operator_handler.py
CMD kopf run --standalone /operator_handler.py
