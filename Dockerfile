# Optional LOCAL-ONLY source image. Compose uses the preloaded IRIS image
# directly, with a read-only source mount, so no runtime build is required.
# Never push an image derived from the restricted EAP runtime to any registry.
ARG IRIS_IMAGE=silentshift-iris:2026.3.0AI.154.0
FROM ${IRIS_IMAGE}
LABEL silentshift.verified-iris-build="2026.3.0AI.154.0 ARM64 Community (154U)"
COPY --chown=irisowner:irisowner src /opt/silentshift/src
COPY --chown=irisowner:irisowner python /opt/silentshift/python
COPY --chown=irisowner:irisowner fixtures /opt/silentshift/fixtures
WORKDIR /opt/silentshift
