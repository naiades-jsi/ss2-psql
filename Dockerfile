# BUILDING: docker build -t <container_name> .
# RUNNING: docker run --network="host" e3ailab/ss2-psql
FROM python:3.9
#RUN apt-get update -y && \
#    apt-get install -y python3-pip python3-dev
COPY . /home/ss2-psql/
WORKDIR "/home/ss2-psql/services/ss2-psql/"
RUN pip3 install -r requirements.txt
CMD ["python3", "index.py"]