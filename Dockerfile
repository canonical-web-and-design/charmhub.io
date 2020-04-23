# syntax=docker/dockerfile:experimental

# Build stage: Install python dependencies
# ===
FROM ubuntu:focal AS python-dependencies
RUN apt-get update && apt-get install --no-install-recommends --yes python3-pip python3-setuptools
ADD requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip3 install --user --requirement /tmp/requirements.txt

# Build stage: Install yarn dependencies
# ===
FROM node:13-slim AS yarn-dependencies
WORKDIR /srv
ADD package.json .
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn yarn install

# Build stage: Run "yarn run build-js"
# ===
FROM yarn-dependencies AS build-js
ADD static/js static/js
ADD webpack.config.js .
RUN yarn run build-js

# Build stage: Run "yarn run build-css"
# ===
FROM yarn-dependencies AS build-css
ADD . .
RUN yarn run build-css

# Set up environment
ENV LANG C.UTF-8
WORKDIR /srv

# Build the production image
# ===
FROM ubuntu:focal

# Install python and import python dependencies
RUN apt-get update && apt-get install --no-install-recommends --yes python3-lib2to3 python3-pkg-resources
COPY --from=python-dependencies /root/.local/lib/python3.8/site-packages /root/.local/lib/python3.8/site-packages
COPY --from=python-dependencies /root/.local/bin /root/.local/bin
ENV PATH="/root/.local/bin:${PATH}"

# Import code, build assets
ADD . .
RUN rm -rf package.json yarn.lock .babelrc webpack.config.js requirements.txt
COPY --from=build-js /srv/static/js static/js
COPY --from=build-css /srv/static/css static/css

# Set build ID
ARG BUILD_ID
ENV TALISKER_REVISION_ID "${BUILD_ID}"


# Setup commands to run server
ENTRYPOINT ["./entrypoint"]
CMD ["0.0.0.0:80"]
