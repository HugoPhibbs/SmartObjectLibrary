# See https://hub.docker.com/r/amazon/aws-lambda-python
FROM amazon/aws-lambda-python:3.12.2025.09.18.13-x86_64
LABEL authors="hugop"

# See https://github.com/awslabs/aws-lambda-web-adapter?tab=readme-ov-file
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

# 8080 is default port for lambda-adapter, but set it here anyhow
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

RUN pip install pipreqs

RUN pip install opensearch-py

RUN pip install gunicorn

COPY . /opt/app

WORKDIR /opt/app

RUN pipreqs src --force --savepath ./requirements.txt

RUN pip install -r requirements.txt

RUN pip install gunicorn

ENTRYPOINT []
CMD ["gunicorn", "-b=0.0.0.0:8080", "-w=1", "src.site.api.main_api:app"]
#CMD ["/bin/bash"]