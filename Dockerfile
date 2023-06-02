FROM camptocamp/qgis-server:3.28

# setup dvc
RUN apt-get update \
    && apt install git -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install dvc[s3] --no-cache

# add dvc
ADD .git /opt/data
ADD .dvc /opt/data/.dvc
ADD data.dvc /opt/data/

ADD entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
