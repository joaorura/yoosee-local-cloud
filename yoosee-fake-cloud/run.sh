#!/usr/bin/with-contenv bashio

HTTP_PORT=8080
REPLY_ACK=true
LOG_LEVEL="info"

if command -v bashio::config >/dev/null 2>&1; then
    if bashio::config.has_value 'http_port'; then
        HTTP_PORT=$(bashio::config 'http_port')
    fi
    if bashio::config.has_value 'reply_ack'; then
        REPLY_ACK=$(bashio::config 'reply_ack')
    fi
    if bashio::config.has_value 'log_level'; then
        LOG_LEVEL=$(bashio::config 'log_level')
    fi
elif [ -f /data/options.json ]; then
    HTTP_PORT=$(jq -r '.http_port // 8080' /data/options.json 2>/dev/null || echo 8080)
    REPLY_ACK=$(jq -r '.reply_ack // true' /data/options.json 2>/dev/null || echo true)
    LOG_LEVEL=$(jq -r '.log_level // "info"' /data/options.json 2>/dev/null || echo "info")
fi

ARGS=("--host" "0.0.0.0" "--http-port" "${HTTP_PORT}")

if [ "${REPLY_ACK}" = "true" ] || [ "${REPLY_ACK}" = "True" ]; then
    ARGS+=("--reply-ack")
fi

if [ "${LOG_LEVEL}" = "debug" ]; then
    ARGS+=("-v")
fi

if command -v bashio::log.info >/dev/null 2>&1; then
    bashio::log.info "Iniciando Yoosee Fake Cloud com porta ${HTTP_PORT}, log_level ${LOG_LEVEL}..."
else
    echo "Iniciando Yoosee Fake Cloud com porta ${HTTP_PORT}, log_level ${LOG_LEVEL}..."
fi

exec yoosee-fake-cloud "${ARGS[@]}"
