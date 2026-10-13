# Harbor config (rendered by setup.sh with envsubst -> installer/harbor.yml).
# Only the keys we change; see installer/harbor.yml.tmpl for every option.

# external_url = http://${SERVER_IP}:8085 . Clients are redirected here to get a
# token (WWW-Authenticate realm), so it must resolve from EVERY client:
# your shell, CI job containers and the k3d nodes. An IP always does.
hostname: ${SERVER_IP}
http:
  port: 8085
# https: omitted on purpose -> plain HTTP (lab only; see the module page).

harbor_admin_password: ${HARBOR_ADMIN_PASSWORD}
database:
  password: ${HARBOR_DB_PASSWORD}
  max_idle_conns: 50
  max_open_conns: 100
  conn_max_lifetime: 5m
  conn_max_idle_time: 0

# Registry blobs, database, redis. Outside the repo, survives `down`.
data_volume: ${HARBOR_DATA}

jobservice:
  max_job_workers: 4
  max_job_duration_hours: 24
  job_loggers: [STD_OUTPUT]
  logger_sweeper_duration: 1

notification:
  webhook_job_max_retry: 3
  webhook_job_http_client_timeout: 3

log:
  level: info
  local:
    rotate_count: 5
    rotate_size: 50M
    location: ${HARBOR_DATA}/logs

_version: 2.15.0

upload_purging:
  enabled: true
  age: 168h
  interval: 24h
  dryrun: false

cache:
  enabled: false
  expire_hours: 24
