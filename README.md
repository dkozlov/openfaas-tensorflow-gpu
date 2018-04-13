# OpenFaas Kubernetes TensorFlow GPU
### Create p2.xlarge AWS EC2 instance with GPU support, with default Ubuntu 16.04 AMI
Request AWS EC2 P2 instances limits from [AWS support](https://console.aws.amazon.com/support/) 

### Prerequisites:
python3
pip3 install ansible

### Configure newly created Ubuntu 16.04
git clone https://github.com/dkozlov/ansible-nvidia
cd ansible-nvidia

### Download private key to ~/.ssh
cp my_aws_ec2_private_key.pem ~/.ssh
chmod 400  ~/.ssh/my_aws_ec2_private_key.pem

### Edit ./ansible.cfg, uncomment prvate_key_file, set correct private_key_file for previously created AWS EC2 instance 
private_key_file = ~/.ssh/my_aws_ec2_private_key.pem

### Create hosts files:
[gpus:vars]
ansible_python_interpreter=/usr/bin/python3

[gpus]
ec2-12-345-67-890.your-region.compute.amazonaws.com #Add previously created GPU hostname 

### Perform initial configuration by ansible, install Dokcer-CE, CUDA, CUDNN, NVIDIA-DOCKER
ansible-playbook gpus.yml

### Check nvidia-smi and docker-ce
```
ansible gpus -m command -a 'bash -lc "nvidia-smi"'
Fri Apr 13 20:36:55 2018       
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 390.30                 Driver Version: 390.30                    |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Tesla K80           Off  | 00000000:00:1E.0 Off |                    0 |
| N/A   40C    P0    72W / 149W |      0MiB / 11441MiB |     99%      Default |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                       GPU Memory |
|  GPU       PID   Type   Process name                             Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+
```

```
ansible gpus -m command -a 'bash -lc "docker --version"'
Docker version 18.03.0-ce, build 0520e24
```
### Install Kubernetes
#ansible gpus -m command -a 'sudo bash -lc "apt-get update && sudo apt-get install -qy docker.io"'

ansible gpus -m command -a 'sudo bash -lc "sudo apt-get update && sudo apt-get install -y apt-transport-https && curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -"'
ansible gpus -m command -a 'sudo bash -lc "echo \"deb http://apt.kubernetes.io/ kubernetes-xenial main\" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list && sudo apt-get update"'
ansible gpus -m command -a 'sudo bash -lc "sudo apt-get update && sudo apt-get install -y kubelet kubeadm kubernetes-cni"'
ansible gpus -m command -a 'sudo bash -lc "wget https://github.com/kubernetes-incubator/cri-tools/releases/download/v1.0.0-beta.0/crictl-v1.0.0-beta.0-linux-amd64.tar.gz; tar -xzvf crictl-*.tar.gz; sudo mv crictl /usr/local/bin"'
ansible gpus -m command -a 'sudo bash -lc "kubeadm init --apiserver-advertise-address={{ inventory_hostname }} --pod-network-cidr=10.244.0.0/16"'
ansible gpus -m command -a 'sudo bash -lc "mkdir -p $HOME/.kube; cp -i /etc/kubernetes/admin.conf $HOME/.kube/config; chown $(id -u):$(id -g) $HOME/.kube/config"'

ansible gpus -m command -a 'sudo bash -lc "kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml"'
ansible gpus -m command -a 'sudo bash -lc "kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/k8s-manifests/kube-flannel-rbac.yml"'
ansible gpus -m command -a 'sudo bash -lc "kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml"'

# allow deployment on gpus node
ansible gpus -m command -a 'sudo bash -lc "kubectl taint nodes --all node-role.kubernetes.io/master-"'

### Install OpenFaas
```
ansible gpus -m command -a 'sudo bash -lc "git clone https://github.com/openfaas/faas-netes"'
ansible gpus -m command -a 'sudo bash -lc "cd faas-netes; kubectl apply -f ./namespaces.yml,./yaml"'
namespace "openfaas" created
namespace "openfaas-fn" created
deployment.apps "alertmanager" created
service "alertmanager" created
configmap "alertmanager-config" created
deployment.apps "faas-netesd" created
service "faas-netesd" created
deployment.apps "gateway" created
service "gateway" created
deployment.apps "nats" created
service "nats" created
deployment.apps "prometheus" created
service "prometheus" created
configmap "prometheus-config" created
deployment.apps "queue-worker" created
serviceaccount "faas-controller" created
role.rbac.authorization.k8s.io "faas-controller" created
rolebinding.rbac.authorization.k8s.io "faas-controller-fn" created
```

### Check OpenFaas services
ansible gpus -m command -a 'sudo bash -lc "kubectl get services -n openfaas"'
NAME           TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
alertmanager   ClusterIP   10.100.190.249   <none>        9093/TCP         2m
faas-netesd    ClusterIP   10.96.61.62      <none>        8080/TCP         2m
gateway        NodePort    10.110.73.148    <none>        8080:31112/TCP   2m
nats           ClusterIP   10.107.19.118    <none>        4222/TCP         2m
prometheus     NodePort    10.110.134.99    <none>        9090:31119/TCP   2m

### 
ansible gpus -m command -a 'sudo bash -lc "git clone https://github.com/openfaas-incubator/python-flask-template"'

### Install faas-cli
ansible gpus -m command -a 'sudo bash -lc "curl -sSL https://cli.openfaas.com | sh"'

