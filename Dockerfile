FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:9a7d-main
#FROM python:3.9-slim-bullseye
RUN pip install latch==2.19.11
RUN mkdir /opt/latch

# Install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        curl \
        unzip \
        git \
        wget \
        bzip2 \
        charliecloud \
        default-jre-headless \
    && apt-get clean autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}

# Install Nextflow
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/bin/ && \
    chmod 777 /usr/bin/nextflow 

SHELL ["bash", "-l" ,"-c"]

# Create workdir for results
RUN mkdir /root/work

# STOP HERE:
# The following lines are needed to ensure your build environement works
# correctly with latch.
COPY wf /root/wf
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
WORKDIR /root