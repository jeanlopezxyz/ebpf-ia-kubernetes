{{/*
Create a default fully qualified app name for kubernetes-dashboard.
*/}}
{{- define "kubernetes-dashboard.fullname" -}}
{{- printf "%s-%s" .Release.Name "kubernetes-dashboard" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels for kubernetes-dashboard
*/}}
{{- define "kubernetes-dashboard.labels" -}}
app.kubernetes.io/name: kubernetes-dashboard
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/part-of: ebpf-ai-platform
app.kubernetes.io/component: dashboard
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end -}}

{{/*
Selector labels for kubernetes-dashboard
*/}}
{{- define "kubernetes-dashboard.selectorLabels" -}}
app.kubernetes.io/name: kubernetes-dashboard
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}