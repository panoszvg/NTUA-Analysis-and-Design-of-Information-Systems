FROM bitnami/python:3.8.10-prod

COPY rhea-pkg ./

RUN pip install -e .

WORKDIR ./examples

CMD ["python3", "setup_area_min.py"]
