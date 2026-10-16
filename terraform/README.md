# Terraform: AWS VPC and EKS

Provisions the network and Kubernetes cluster that Campus Patrol runs on.

```text
AWS (ap-south-1)
 └── VPC 10.20.0.0/16
      ├── 2 public subnets   (load balancers, NAT gateway)
      ├── 2 private subnets  (worker nodes)
      └── EKS cluster
           └── managed node group (t3.medium, 2-4 nodes)
                + add-ons: coredns, kube-proxy, vpc-cni, aws-ebs-csi-driver
```

The EBS CSI driver is required: without it the PostgreSQL PersistentVolumeClaim stays `Pending`.

> **Cost warning.** The EKS control plane, NAT gateway and nodes bill by the hour (roughly USD 0.15 to 0.30/hour all in). Run `terraform destroy` as soon as you have your screenshots.

## Usage

Credentials come from your environment (`aws configure` or `AWS_PROFILE`), never from files in this repo.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # optional; defaults work
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan
terraform apply                                # takes ~15 minutes
$(terraform output -raw configure_kubectl)     # point kubectl at the cluster
kubectl get nodes
```

Tear down. Delete the Helm release first so the load balancer it created does not block VPC deletion:

```bash
helm uninstall ingress-nginx -n ingress-nginx
terraform destroy
```

`terraform.tfvars`, state files and `.terraform/` are git-ignored. `.terraform.lock.hcl` is committed to pin provider versions.
