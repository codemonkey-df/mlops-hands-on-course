{{/*
Files starting with "_" are not rendered as manifests: they hold reusable
named templates. Call them with  {{ include "postgres.fullname" . }}
The "." passed in is the root context (Values, Release, Chart, ...).
*/}}

{{/* Name of every object: the release name, e.g. `helm install postgres ...` -> "postgres" */}}
{{- define "postgres.fullname" -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Labels that identify pods. Used in selectors, so they must never change. */}}
{{- define "postgres.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/* Full label set: selector labels + informational ones (these may change). */}}
{{- define "postgres.labels" -}}
{{ include "postgres.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}
