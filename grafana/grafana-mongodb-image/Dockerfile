FROM docker.io/bitnami/minideb:buster
LABEL maintainer "Bitnami <containers@bitnami.com>"

ENV HOME="/" \
    OS_ARCH="amd64" \
    OS_FLAVOUR="debian-10" \
    OS_NAME="linux"

COPY prebuildfs /
# Install required system packages and dependencies
RUN install_packages acl ca-certificates curl gzip libc6 libfontconfig procps tar wget npm
RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "grafana" "8.3.3-1" --checksum 58cd2bbf087e5b95e065576d54c429ac82e293a8fe583862eb75f982d31b3fa0
RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "gosu" "1.14.0-1" --checksum 16f1a317859b06ae82e816b30f98f28b4707d18fe6cc3881bff535192a7715dc
RUN chmod g+rwX /opt/bitnami

COPY rootfs /
RUN /opt/bitnami/scripts/grafana/postunpack.sh
ENV BITNAMI_APP_NAME="grafana" \
    BITNAMI_IMAGE_VERSION="8.3.3-debian-10-r28" \
    PATH="/opt/bitnami/grafana/bin:/opt/bitnami/common/bin:$PATH"

# Go to the default plugins directory
# WORKDIR /var/lib/grafana/plugins

# Download the plugin repo and uncompress it
# RUN wget https://github.com/JamesOsgood/mongodb-grafana/archive/master.tar.gz -O - | tar xz

# Go inside plugin directory
# WORKDIR /var/lib/grafana/plugins/mongodb-grafana-master

# Install npm packages
# RUN npm install --silent

EXPOSE 3000
EXPOSE 3333

WORKDIR /opt/bitnami/grafana
USER 1001
# Download the plugin repo and uncompress it
RUN mkdir /opt/bitnami/grafana/plugins
RUN wget https://github.com/JamesOsgood/mongodb-grafana/archive/master.tar.gz -O - | tar xz -C /opt/bitnami/grafana/plugins

USER root
# Install npm packages
RUN cd /opt/bitnami/grafana/plugins/mongodb-grafana-master && npm install
USER 1001

ENTRYPOINT [ "/opt/bitnami/scripts/grafana/entrypoint.sh" ]
CMD [ "/opt/bitnami/scripts/grafana/run.sh" ]
