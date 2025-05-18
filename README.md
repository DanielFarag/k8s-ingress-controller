# Custom Ingress-like Controller for Kubernetes (POC)

> It is a simplified reimplementation of an Ingress controller using Kubernetes Custom Resource Definitions (CRDs) and NGINX to help understand controller design patterns, custom resource handling, and dynamic configuration in Kubernetes.

## 🧩 Project Structure

### Example Ingress Entries:

```yaml
apiVersion: daniel.iti.com/v1
kind: IngressEntry
metadata:
  name: ingress-entry-1
spec:
  path: /nginx1
  service: nginx-service1
  port: 80
```
---

### 3. Controller

A Python script (`main.py`) handles:

* Watching for changes to `IngressEntry` resources
* Storing the entries in a SQLite DB (`database.sqlite`)
* Re-generating the NGINX config and updating the NGINX pod via a `ConfigMap`

#### Pseudo-Workflow:

1. Watch for events (`ADDED`, `MODIFIED`, `DELETED`) from the K8s API.
2. Store/update/delete entries in SQLite.
3. Render an NGINX config using all current entries.
4. Mount config into the NGINX pod to reflect new routing rules.

---

### 4. NGINX Deployment

An NGINX container is deployed with:

* A mounted config file (`/etc/nginx/conf.d/default.conf`)
* Config generated dynamically from CRD entries via a `ConfigMap`

---

## 🔧 Future Improvements

* Add support for host-based routing
* Enable HTTPS with Let's Encrypt
* Validate services before writing config
* Auto-reload NGINX config without pod restart
