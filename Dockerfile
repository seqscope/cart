###################
# GDAL 
###################

FROM osgeo/gdal:ubuntu-full-latest as builder

WORKDIR /app
ADD pyproject.toml poetry.lock /app/

# RUN apt-get install build-base libffi-dev
RUN apt-get update -y \
	&& apt-get install -y python3-pip python-dev build-essential 
RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-ansi


# deploy

FROM osgeo/gdal:ubuntu-full-latest
WORKDIR /app

COPY --from=builder /app /app
ADD . /app

RUN adduser app -h /app -u 1000 -g 1000 -DH
USER 1000

# CMD /app/.venv/bin/python -m geneus_loci.meta


# #################
# # Tippecanoe
# #################
#
# # Update repos and install dependencies
# RUN apt-get update \
#   && apt-get -y upgrade \
#   && apt-get -y install git build-essential libsqlite3-dev zlib1g-dev
#
# # Create a directory and copy in all files
# RUN mkdir -p /tmp/tippecanoe-src
# RUN git clone https://github.com/mapbox/tippecanoe.git /tmp/tippecanoe-src
# WORKDIR /tmp/tippecanoe-src
#
# # Build tippecanoe
# RUN make \
#   && make install
#
# WORKDIR /
# RUN rm -rf /tmp/tippecanoe-src \
#   && apt-get -y remove --purge build-essential && apt-get -y autoremove
