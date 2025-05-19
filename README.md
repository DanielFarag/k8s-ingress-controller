# Custom Ingress-like Controller for Kubernetes (POC)

> It is a simplified reimplementation of an Ingress controller using Kubernetes Custom Resource Definitions (CRDs) and NGINX to help understand controller design patterns, custom resource handling, and dynamic configuration in Kubernetes.

## 🧩 Project Structure

### Example Ingress Entries:
#### Setup Controller
```sh
kubectl apply -f https://raw.githubusercontent.com/DanielFarag/k8s-ingress-controller/main/sample/controller.yaml
```
#### Test Services
```sh
kubectl apply -f https://raw.githubusercontent.com/DanielFarag/k8s-ingress-controller/main/sample/services.yaml
```
> This will create 2 services [ apache and caddy ] .

##### 1- Apache Service
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: httpd
spec:
  selector:
    matchLabels:
      app: httpd
  template:
    metadata:
      labels:
        app: httpd
    spec:
      containers:
      - name: httpd
        image: httpd:alpine
        resources:
          requests:
            memory: "128Mi"
            cpu: "500m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: apache-service
spec:
  selector:
    app: httpd
  ports:
  - port: 80
    targetPort: 80
```
##### 2- Caddy Service
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: caddy
spec:
  selector:
    matchLabels:
      app: caddy
  template:
    metadata:
      labels:
        app: caddy
    spec:
      containers:
      - name: caddy
        image: caddy:latest
        resources:
          requests:
            memory: "128Mi"
            cpu: "500m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: caddy-service
spec:
  selector:
    app: caddy
  ports:
  - port: 81
    targetPort: 80
```

##### 3- Create 2 entries
```sh
kubectl apply -f https://raw.githubusercontent.com/DanielFarag/k8s-ingress-controller/main/sample/entry1.yaml
kubectl apply -f https://raw.githubusercontent.com/DanielFarag/k8s-ingress-controller/main/sample/entry2.yaml
```
> This will create 2 entries for the previously created services [ apache and caddy ] .

```yaml
apiVersion: daniel.iti.com/v1
kind: IngressEntry
metadata:
  name: ingress-entry-1
spec:
  path: /apache
  service: apache-service
  port: 80
```
---

### Controller

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

### NGINX Deployment

An NGINX container is deployed with:

* A mounted config file (`/etc/nginx/conf.d/default.conf`)
* Config generated dynamically from CRD entries via a `ConfigMap`

---

## 🔧 Future Improvements

* [ ] Add support for host-based routing
* [ ] Enable HTTPS with Let's Encrypt
* [ ] Validate services before writing config
* [x] Auto-reload NGINX config without pod restart
