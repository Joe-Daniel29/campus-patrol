{{/* Base name shared by every resource: <release>-campus-patrol, or just the release if it already contains the chart name. */}}
{{- define "patrol.fullname" -}}
{{- if contains .Chart.Name .Release.Name -}}
{{- .Release.Name | trunc 40 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 40 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/* Labels common to all resources. */}}
{{- define "patrol.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{/* Labels that select the pods of one component. Usage: include "patrol.selector" (dict "ctx" . "component" "backend") */}}
{{- define "patrol.selector" -}}
app.kubernetes.io/name: {{ .ctx.Chart.Name }}
app.kubernetes.io/instance: {{ .ctx.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{- define "patrol.postgresSecret" -}}
{{ include "patrol.fullname" . }}-postgres
{{- end -}}

{{- define "patrol.appSecret" -}}
{{ include "patrol.fullname" . }}-app
{{- end -}}
