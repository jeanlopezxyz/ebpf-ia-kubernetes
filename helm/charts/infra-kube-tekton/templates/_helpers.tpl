{{/*
Common labels for all Tekton components
*/}}
{{- define "tekton.labels" -}}
app.kubernetes.io/name: {{ include "tekton.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/part-of: tekton-platform
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ include "tekton.chart" . }}
{{- end -}}

{{/*
Common selector labels for all Tekton components
*/}}
{{- define "tekton.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tekton.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Chart name
*/}}
{{- define "tekton.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Chart full name
*/}}
{{- define "tekton.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Chart name and version as used by the chart label
*/}}
{{- define "tekton.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Dashboard specific helpers
*/}}
{{- define "tekton.dashboard.name" -}}
{{- printf "%s-dashboard" (include "tekton.name" .) -}}
{{- end -}}

{{- define "tekton.dashboard.fullname" -}}
{{- printf "%s-dashboard" (include "tekton.fullname" .) -}}
{{- end -}}

{{- define "tekton.dashboard.labels" -}}
{{ include "tekton.labels" . }}
app.kubernetes.io/component: dashboard
{{- end -}}

{{- define "tekton.dashboard.selectorLabels" -}}
{{ include "tekton.selectorLabels" . }}
app.kubernetes.io/component: dashboard
{{- end -}}

{{/*
Service Account Names
*/}}
{{- define "tekton.dashboard.serviceAccountName" -}}
{{- if .Values.dashboard.serviceAccount.name -}}
{{- .Values.dashboard.serviceAccount.name -}}
{{- else -}}
{{- include "tekton.dashboard.fullname" . -}}
{{- end -}}
{{- end -}}

{{/*
Namespace helper
*/}}
{{- define "tekton.namespace" -}}
{{- default .Release.Namespace .Values.global.namespace -}}
{{- end -}}