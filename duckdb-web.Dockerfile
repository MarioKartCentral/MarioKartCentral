FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    ca-certificates \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Download and install DuckDB CLI (latest version)
RUN wget -q https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip \
    && unzip duckdb_cli-linux-amd64.zip \
    && mv duckdb /usr/local/bin/duckdb \
    && chmod +x /usr/local/bin/duckdb \
    && rm duckdb_cli-linux-amd64.zip

# Create data directory
RUN mkdir -p /data

# Expose port 4213 (DuckDB's default web UI port)
EXPOSE 4213

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting DuckDB UI Server..."\n\
duckdb "$1" -c "CALL start_ui_server();" &\n\
echo "DuckDB UI Server started, keeping container alive..."\n\
while true; do sleep 30; done' > /usr/local/bin/start-duckdb.sh && \
    chmod +x /usr/local/bin/start-duckdb.sh

# Set working directory
WORKDIR /data

# Default command to start DuckDB with UI server
CMD ["/usr/local/bin/start-duckdb.sh"]
