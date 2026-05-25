# ═══════════════════════════════════════════════════════════════════
#  Dockerfile — Apache Flume 1.11 with Python 3 & Hadoop 3.3 client
# ═══════════════════════════════════════════════════════════════════
FROM eclipse-temurin:11-jre-jammy

LABEL maintainer="Group-20"
LABEL description="Apache Flume 1.11 agent with HDFS sink support"

# ── Build-time arguments ───────────────────────────────────────────
ARG FLUME_VERSION=1.11.0
ARG HADOOP_VERSION=3.3.6
ARG FLUME_MIRROR=https://archive.apache.org/dist/flume
ARG HADOOP_MIRROR=https://archive.apache.org/dist/hadoop/core

ENV FLUME_HOME=/opt/flume
ENV HADOOP_HOME=/opt/hadoop
ENV PATH="${FLUME_HOME}/bin:${HADOOP_HOME}/bin:${PATH}"
ENV JAVA_HOME=/opt/java/openjdk
# Increase JVM heap — Hadoop classpath contains hundreds of JARs
ENV JAVA_OPTS="-Xms256m -Xmx512m"
ENV FLUME_JAVA_OPTS="-Xms256m -Xmx512m"

# ── System dependencies ────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
      wget \
      curl \
      python3 \
      python3-pip \
      netcat-openbsd \
      procps \
    && rm -rf /var/lib/apt/lists/*

# ── Download & install Apache Flume ───────────────────────────────
RUN wget -q "${FLUME_MIRROR}/${FLUME_VERSION}/apache-flume-${FLUME_VERSION}-bin.tar.gz" \
      -O /tmp/flume.tar.gz \
    && tar -xzf /tmp/flume.tar.gz -C /opt \
    && mv /opt/apache-flume-${FLUME_VERSION}-bin ${FLUME_HOME} \
    && rm /tmp/flume.tar.gz

# ── Download Hadoop client libs (only what Flume HDFS sink needs) ─
RUN wget -q "${HADOOP_MIRROR}/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz" \
      -O /tmp/hadoop.tar.gz \
    && tar -xzf /tmp/hadoop.tar.gz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
    && rm /tmp/hadoop.tar.gz

# Copy Hadoop HDFS jars into Flume's lib directory
RUN cp ${HADOOP_HOME}/share/hadoop/hdfs/*.jar          ${FLUME_HOME}/lib/ && \
    cp ${HADOOP_HOME}/share/hadoop/hdfs/lib/*.jar      ${FLUME_HOME}/lib/ && \
    cp ${HADOOP_HOME}/share/hadoop/common/*.jar        ${FLUME_HOME}/lib/ && \
    cp ${HADOOP_HOME}/share/hadoop/common/lib/*.jar    ${FLUME_HOME}/lib/ && \
    cp ${HADOOP_HOME}/share/hadoop/mapreduce/*.jar     ${FLUME_HOME}/lib/ 2>/dev/null || true

# ── Flume configuration & scripts ─────────────────────────────────
COPY flume.conf          ${FLUME_HOME}/conf/flume.conf
COPY core-site.xml       ${HADOOP_HOME}/etc/hadoop/core-site.xml
COPY generate_logs.py    /opt/generate_logs.py
COPY flume-entrypoint.sh /opt/flume-entrypoint.sh

RUN chmod +x /opt/flume-entrypoint.sh && \
    mkdir -p /opt/spooling_dir && \
    mkdir -p ${FLUME_HOME}/logs

# ── Expose Flume monitoring port ──────────────────────────────────
EXPOSE 41414

WORKDIR /opt/flume

ENTRYPOINT ["/opt/flume-entrypoint.sh"]
