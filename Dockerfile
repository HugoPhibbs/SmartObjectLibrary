FROM python:3.12-slim
LABEL authors="hugop"

RUN pip install pipreqs

RUN pip install opensearch-py

COPY . /opt/app

WORKDIR /opt/app

RUN pipreqs src --force --savepath ./requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "5000", "--fill-opensearch"]
#CMD ["/bin/bash"]