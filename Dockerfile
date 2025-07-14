FROM mambaorg/micromamba:git-480b0fa-alpine3.18
LABEL authors="hugop"
USER root

RUN micromamba create -n spl

RUN micromamba run -n spl micromamba install -y -c conda-forge \
    ifcopenshell \
    flask \
    flask-cors \
    python-dotenv \
    opensearch-py \
    pydash \
    lark

RUN mkdir "/opt/app"
COPY . /opt/app

WORKDIR /opt/app

EXPOSE 5000
CMD ["micromamba", "run", "-n", "spl", "python", "main.py"]