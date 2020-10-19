FROM python:3.8-slim as python-builder-38

LABEL maintainer="giaduongducminh@gmail.com"
LABEL service_name="python-builder"

RUN mkdir /install
WORKDIR /install
COPY Pipfile* ./
RUN apt-get update && apt-get install -y pipenv  \
    && pip install --upgrade pip && pipenv lock -r > requirements.txt \
    && pip install --prefix=/install --ignore-installed -r requirements.txt \
    && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/

FROM python:3.8-alpine3.12

LABEL maintainer="giaduongducminh@gmail.com"
LABEL service_name="git-operator"

RUN adduser --disabled-password -u 1000 git-ops
USER git-ops

WORKDIR /app
COPY --from=python-builder-38 /install /usr/local
ADD ./git_operator/*.py /app/

ENTRYPOINT [ "/usr/local/bin/python", "-m", "main" ]
