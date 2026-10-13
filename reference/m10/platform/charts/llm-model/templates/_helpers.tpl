{{- define "llm.fullname" -}}{{ .Release.Name | trunc 63 | trimSuffix "-" }}{{- end -}}

{{- define "llm.selectorLabels" -}}
app.kubernetes.io/name: llm-model
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "llm.labels" -}}
{{ include "llm.selectorLabels" . }}
llm.mlops/model: {{ .Values.model.servedName }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{/* Pick the mock or the real image */}}
{{- define "llm.image" -}}
{{- $i := ternary .Values.image.mock .Values.image.real .Values.mock -}}
{{ $i.repository }}:{{ $i.tag }}
{{- end -}}
