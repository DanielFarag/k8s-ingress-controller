from kubernetes import client, config, watch

from kubernetes.client.rest import ApiException
from os import path
import yaml

class K8S:
    def __init__(self):
        config.load_incluster_config()

    def createCrd(self):
        try:
            crd=path.join(path.dirname(__file__), "deployments/crd.yaml")
            
            with open(crd) as f:
                nginx_crd = yaml.safe_load(f)

                api_ext = client.ApiextensionsV1Api()
                try:
                    resp = api_ext.create_custom_resource_definition(body=nginx_crd)
                    print(f"CRD created. Status='{resp.metadata.name}'")
                except ApiException as e:
                    if e.status == 409:
                        print("CRD already exists, skipping creation.")
                    else:
                        print(f"Failed to create CRD: {e}")
                        raise
        except Exception as e:
            print(f"CRD creation error: {e}")
            return []

    def stream(self):
        api = client.CustomObjectsApi()

        group = "daniel.iti.com"
        version = "v1"
        namespace = "default"
        plural = "ingress-entries"

        w = watch.Watch()

        print(f"Watching for new {plural} in namespace '{namespace}'...")

        for event in w.stream(api.list_namespaced_custom_object, group, version, namespace, plural):
            obj = event['object']
            yield {
                "action": event['type'],
                "data": {
                    "id": obj['metadata']['uid'],
                    "service": obj['spec']['service'],
                    "port": obj['spec']['path'].strip('/'),
                    "path": obj['spec']['port'],
                }
            }
                

    def configureNginx(self, entries):
        template = """
        location /{path} {{
            proxy_pass http://{service}:{port}/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
    """
        content = ""

        for entry in entries:
            content += template.format(service=entry[1], path=entry[2].strip('/'), port=entry[3])


        ref=path.join(path.dirname(__file__), "nginx/ref.conf")

        with open(ref) as f:
            ref = f.read()

        nginx_conf_content = ref.format(entries=content)

        v1 = client.CoreV1Api()
        config_map = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(name="nginx-config"),
            data={"default.conf": nginx_conf_content}
        )

        print(nginx_conf_content)
        try:
            v1.replace_namespaced_config_map("nginx-config", "default", config_map)
        except client.exceptions.ApiException:
            v1.create_namespaced_config_map("default", config_map)

            
        self.nginxDeplyoment()
        self.nginxService()

    def nginxDeplyoment(self):
        
        depyloment=path.join(path.dirname(__file__), "deployments/nginx.yaml")

        with open(depyloment) as f:
            dep = yaml.safe_load(f)

        api = client.AppsV1Api()

        namespace = dep.get('metadata', {}).get('namespace', 'default')
        name = dep['metadata']['name']


        try:
            existing_deployment = api.read_namespaced_deployment(name=name, namespace=namespace)

            depyloment['metadata']['resourceVersion'] = existing_deployment.metadata.resource_version

            api.replace_namespaced_deployment(name=name, namespace=namespace, body=depyloment)
        except ApiException as e:
            if e.status == 404:
                api.create_namespaced_deployment(namespace=namespace, body=depyloment)
            else:
                print(e)
                raise 
        print(f"Deployment '{name}' created")

    def nginxService(self):
        
        depyloment=path.join(path.dirname(__file__), "deployments/nginx-service.yaml")

        with open(depyloment) as f:
            dep = yaml.safe_load(f)

        api = client.CoreV1Api()

        namespace = dep.get('metadata', {}).get('namespace', 'default')
        name = dep['metadata']['name']

        try:
            api.delete_namespaced_service(name=name, namespace=namespace)
        except client.exceptions.ApiException as e:
            pass
        api.create_namespaced_service(namespace=namespace, body=dep)
        print(f"Service '{name}' created")
