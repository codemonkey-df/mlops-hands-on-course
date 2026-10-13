#!/usr/bin/env bash
# Helpers for the M7 checks (sourced).
source "$COURSE_ROOT/exercises/_lib.sh"
ROBOTS="$COURSE_ROOT/infra/compose/harbor/robots.env"
[[ -f "$ROBOTS" ]] || fail "run infra/compose/harbor/bootstrap.sh first (robots.env missing)"
# shellcheck disable=SC1090
source "$ROBOTS"
harbor_login() { printf '%s' "$HARBOR_CI_SECRET" | docker login 127.0.0.1:8085 -u "$HARBOR_CI_USER" --password-stdin >/dev/null; }
pull_secret() { # namespace
  kubectl -n "$1" create secret docker-registry harbor-pull --docker-server=harbor.local:8085 \
    --docker-username="$HARBOR_K8S_USER" --docker-password="$HARBOR_K8S_SECRET" >/dev/null
  kubectl -n "$1" patch serviceaccount default -p '{"imagePullSecrets":[{"name":"harbor-pull"}]}' >/dev/null
}
run_pod() { # namespace name image -> prints the pod's log, fails on pull errors
  local ns="$1" name="$2" image="$3"
  kubectl -n "$ns" run "$name" --image="$image" --image-pull-policy=Always --restart=Never >/dev/null
  for _ in $(seq 30); do
    phase=$(kubectl -n "$ns" get pod "$name" -o jsonpath='{.status.phase}')
    [[ "$phase" == Succeeded ]] && { kubectl -n "$ns" logs "$name"; return 0; }
    reason=$(kubectl -n "$ns" get pod "$name" -o jsonpath='{.status.containerStatuses[0].state.waiting.reason}')
    if [[ "$reason" == ErrImagePull || "$reason" == ImagePullBackOff ]]; then
      kubectl -n "$ns" get events --field-selector involvedObject.name="$name" -o jsonpath='{range .items[*]}{.message}{"\n"}{end}' | grep -i fail | tail -1 | cut -c1-300
      return 1
    fi
    sleep 2
  done
  return 1
}
