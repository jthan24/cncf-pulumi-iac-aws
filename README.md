# cncf-pulumi-iac-aws

## Prereqs

- python 3
- `sudo apt install python3.8-venv -y`

## Installation

### Install aws-cli
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Install pulumi
```bash
curl -fsSL https://get.pulumi.com | sh
export PATH=$PATH:/home/ubuntu/.pulumi/bin
pulumi version
```


## Optional - Create resources from scratch

### Python
```bash
mkdir -p src/python && cd src/python && pulumi new aws-python --name awsImpl
# Follow the instructions and select at the end a aws-python
```

### YAML
```bash
mkdir -p src/yaml && cd src/yaml && pulumi new aws-yaml --name awsImpl
```



## Start using this repository
```bash

```






# References
https://www.pulumi.com/docs/clouds/aws/get-started/begin/
https://www.pulumi.com/docs/concepts/how-pulumi-works/
https://www.pulumi.com/docs/clouds/aws/
https://www.pulumi.com/resources/
https://github.com/pulumi/training
https://www.pulumi.com/templates/
https://github.com/pulumi/templates
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html