FROM python:3.12-slim
LABEL authors="hugop"

RUN pip install pipreqs

RUN pip install opensearch-py

COPY . /opt/app

WORKDIR /opt/app

RUN pipreqs src/site/ --force --savepath ./site_requirements.txt

RUN pip install -r site_requirements.txt

CMD ["python", "-m", "src.site.api.main_api", "--host", "0.0.0.0", "--port", "5000"]
#CMD ["/bin/bash"]