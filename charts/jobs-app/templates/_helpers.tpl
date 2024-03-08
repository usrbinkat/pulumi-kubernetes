{{/*
Render full image name from given values, e.g:
```
image:
  repository: quay.io/isovalent/hubble-rbac
  override:
  tag: latest
  useDigest: true
  digest: abcdefgh
```
Then `include "jobs-app.image" .Values.server.rbac.image`
will return `quay.io/isovalent/hubble-rbac:latest@abcdefgh`.
If `override` is included that value only will be returned.
*/}}
{{- define "jobs-app.image" -}}
{{- $digest := (.useDigest | default false) | ternary (printf "@%s" .digest) "" -}}
{{- if .override -}}
{{- printf "%s" .override -}}
{{- else -}}
{{- printf "%s:%s%s" .repository .tag $digest -}}
{{- end -}}
{{- end -}}
