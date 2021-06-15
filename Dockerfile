FROM ubuntu:20.04 as base 
USER root

## Setting default environment variables
ENV WEB_ROOT=/web_root
ENV APP_ROOT=${WEB_ROOT}/afs
# Root project folder
ENV ARCHES_ROOT=${WEB_ROOT}/arches
ENV WHEELS=/wheels
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y make software-properties-common

FROM base as wheelbuilder

WORKDIR ${WHEELS}

# Install pip requirements files
COPY ./arches/arches/install/requirements.txt ${WHEELS}/requirements.txt
COPY ./arches/arches/install/requirements_dev.txt ${WHEELS}/requirements_dev.txt

# Install packages required to build the python libs, then remove them
RUN set -ex \
    && BUILD_DEPS=" \
        build-essential \
        libxml2-dev \
        libproj-dev \
        libjson-c-dev \
        xsltproc \
        docbook-xsl \
        docbook-mathml \
        libgdal-dev \
        libpq-dev \
        python3.8 \
        python3.8-dev \
        curl \
        python3.8-distutils \
        libldap2-dev libsasl2-dev ldap-utils \
        dos2unix \
        " \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.8 get-pip.py

RUN pip3 wheel --no-cache-dir -b /tmp -r ${WHEELS}/requirements.txt  \
    && pip3 wheel --no-cache-dir -b /tmp gunicorn \
    && pip3 wheel --no-cache-dir -b /tmp django-auth-ldap

COPY ./afs/afs/install/requirements.txt ${WHEELS}/project_requirements.txt

RUN pip3 wheel --no-cache-dir -b /tmp -r ${WHEELS}/project_requirements.txt

# Add Docker-related files
COPY /afs/docker/entrypoint.sh ${WHEELS}/entrypoint.sh
RUN chmod -R 700 ${WHEELS} &&\
  dos2unix ${WHEELS}/*.sh

FROM base 

# Get the pre-built python wheels from the build environment
RUN mkdir ${WEB_ROOT}

COPY --from=wheelbuilder ${WHEELS} /wheels

# Install packages required to run Arches
# Note that the ubuntu/debian package for libgdal1-dev pulls in libgdal1i, which is built
# with everything enabled, and so, it has a huge amount of dependancies (everything that GDAL
# support, directly and indirectly pulling in mysql-common, odbc, jp2, perl! ... )
# a minimised build of GDAL could remove several hundred MB from the container layer.
RUN set -ex \
    && RUN_DEPS=" \
        build-essential \
        python3.8-dev \
        mime-support \
        libgdal-dev \
        python3-venv \
        postgresql-client-12 \
        python3.8 \
        python3.8-distutils \
        python3.8-venv \
    " \
    && apt-get install -y --no-install-recommends curl \
    && curl -sL https://deb.nodesource.com/setup_10.x | bash - \
    && curl -sL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -sc)-pgdg main" \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $RUN_DEPS \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.8 get-pip.py \
    && apt-get install -y nodejs \
    && npm install -g yarn

# Install Yarn components
RUN mkdir -p ${APP_ROOT}/afs/app/media/packages
WORKDIR ${APP_ROOT}/afs
RUN yarn install

## Install virtualenv
WORKDIR ${WEB_ROOT}

RUN mv ${WHEELS}/entrypoint.sh entrypoint.sh

# RUN python3.8 -m venv ENV \
#     && . ENV/bin/activate \
RUN pip install requests \
    # && pip install -f ${WHEELS} django-auth-ldap \
    # && pip install -f ${WHEELS} gunicorn \
    # && pip install -r ${WHEELS}/project_requirements.txt \
                #    -f ${WHEELS} \
    && rm -rf ${WHEELS} \
    && rm -rf /root/.cache/pip/*

# Install the Arches application
# FIXME: ADD from github repository instead?
COPY ./arches ${ARCHES_ROOT}

# From here, run commands from ARCHES_ROOT
WORKDIR ${ARCHES_ROOT}

# RUN . ../ENV/bin/activate \
    # && 

RUN pip install -e .

RUN mkdir /var/log/supervisor
RUN mkdir /var/log/celery

# Set default workdir
WORKDIR ${APP_ROOT}

# # Set entrypoint
ENTRYPOINT ["../entrypoint.sh"]
CMD ["run_arches"]

# Expose port 8000
EXPOSE 8000