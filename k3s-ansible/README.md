## Getting Started

This guide walks you through installing **k3s** using Ansible with my custom method.

### Prerequisites

* Clone the official k3s-ansible by k3s-io repository:
  ```sh
  git clone https://github.com/k3s-io/k3s-ansible.git
  cd k3s-ansible
  ```

### Installation with Ansible Linux

1. Prepare Inventory File
*  Copy the sample inventory file:
   ```sh
   cp inventory-sample.yml inventory.yml
   ```
* Edit ```inventory.yml``` as needed to match your environment (hosts, users, etc.).

2. Enable Unattended SSH Access
   ```sh
   ssh-keygen
   ssh-copy-id <user>@<host-IP>
   ```

3. Run the Ansible Playbook
   ```sh
   ansible-playbook playbooks/site.yml -i inventory.yml
   ```

4. SSH to VM and Customize Systemd
* Edit the k3s systemd service file:
   ```sh
   sudo nano /etc/systemd/system/k3s.service
   ```
* Locate the ```ExecStart``` line and append the following options at the end:
   ```sh
   --tls-san <host-IP> --disable traefik
   ```
* Save and reload the systemd daemon:
   ```sh
   sudo systemctl daemon-reload
   sudo systemctl restart k3s
   ```

5. Install cert-manager CRDs and Components
   ```sh
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.crds.yaml
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
   ```

6. Install NGINX Ingress Controller with Helm
* Add the ingress-nginx Helm repository:
   ```sh
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   ```
* Install ingress-nginx with admission webhooks disabled:
   ```sh
    helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx --create-namespace
   ```
* If your Ingress is not secure or the ACME challenge fails (certificate cannot be issued), you can bypass with this:
  ```sh
  kubectl delete validatingwebhookconfiguration ingress-nginx-admission -n ingress-nginx
  ```

7. Deploy Cluster Issuer
* Replace the `<email>` placeholder with your actual email address in `cluster-issuer.yaml`.
* Then apply the manifest:
   ```sh
   kubectl apply -f cluster-issuer.yaml
   ```

### Installation with Docker

1. Prepare Inventory File
*  Copy the sample inventory file:
   ```sh
   cp inventory-sample.yml inventory.yml
   ```
* Edit ```inventory.yml``` as needed to match your environment (hosts, users, etc.).

2. Use Ansible Inside Docker Container
* Start the container using Docker Compose:
   ```sh
   docker compose up -d
   ```
* Enter the container:
   ```sh
   docker exec -it k3s-ansible bash 
   ```
* Set up unattended SSH access:
   ```sh
   ssh-keygen
   ssh-copy-id <user>@<host-IP>
   ```

3. Run the Playbook
* From inside the container, run:
   ```sh
   ansible-playbook playbooks/site.yml -i inventory.yml
   ```
* After the playbook completes, you can stop and remove the container if desired.

✅ **Note:** After completed, continue with steps 4 to 7 same as Ansible Linux Installation.

### Ingress

* Ingress Template:
```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: <ingress-name>
  namespace: <namespace>
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-cert
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - <example.host.com>
    secretName: <cert-name>
  rules:
  - host: <example.host.com>
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: <service-name>
            port:
              number: <service-port>

```
