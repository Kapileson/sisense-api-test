FROM python:3.7.7-slim-buster
RUN apt-get update
# copy file
WORKDIR /app
COPY ./ /app

ENV GOOGLE_APPLICATION_CREDENTIALS="/app/gcp_credentials.json"
ENTRYPOINT ["/bin/bash", "build/install.sh", "apitest"]

