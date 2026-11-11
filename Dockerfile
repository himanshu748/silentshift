# Local-only EAP derivative: never push this image to any registry.
ARG IRIS_IMAGE=silentshift-iris:2026.3.0AI.154.0
FROM ${IRIS_IMAGE}
LABEL silentshift.verified-iris-build="2026.3.0AI.154.0 ARM64 Community (154U)"
COPY --chown=irisowner:irisowner src /opt/silentshift/src
COPY --chown=irisowner:irisowner python /opt/silentshift/python
COPY --chown=irisowner:irisowner fixtures /opt/silentshift/fixtures
WORKDIR /home/irisowner

COPY --chown=irisowner:irisowner java /opt/silentshift/java
USER root
RUN mkdir -p /opt/silentshift-pex && chown irisowner:irisowner /opt/silentshift-pex
USER irisowner
RUN sh /opt/silentshift/java/build.sh /opt/silentshift/java /opt/silentshift-pex
