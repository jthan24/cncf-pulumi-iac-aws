"""An AWS Python Pulumi program"""

from pulumi import Config, Output, export
from pulumi_aws import ec2, iam
import json

config = Config()
values = config.require_object("values")
proyecto = values.get("proyecto")

## Creacion de la VPC

main = ec2.Vpc("vpc-devops-"+proyecto, 
    cidr_block=values.get("vpc_address")
    )

## Creacion de las subnets

zonas_priv = []
for i in range(len(values.get("subnet_priv_address"))):
    zonas_priv.append(ec2.Subnet("devops-priv-subnet-"+str(i),
        vpc_id=main.id,
        availability_zone=values.get("subnet_zones")[i],
        cidr_block=values.get("subnet_priv_address")[i],
        tags=values.get("tags")
    ))

zonas_pub = []
for i in range(len(values.get("subnet_pub_address"))):
    zonas_pub.append(ec2.Subnet("devops-pub-subnet-"+str(i),
        vpc_id=main.id,
        availability_zone=values.get("subnet_zones")[i],
        cidr_block=values.get("subnet_pub_address")[i],
        map_public_ip_on_launch=True,
        tags=values.get("tags")
    ))
    

defaultRoute = ec2.DefaultRouteTable("devops-routetable-default"+proyecto,
    default_route_table_id=main.default_route_table_id,
    tags=values.get("tags")
    )

igw = ec2.InternetGateway("devops-igw-"+proyecto,
    vpc_id=main.id,
    tags=values.get("tags")
    )

routeTable = ec2.RouteTable("devops-route-table"+proyecto,
    vpc_id=main.id,
    routes=[
        ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        )
    ],
    tags=values.get("tags")
    )


routeTableAssoc = []
for i in range(len(zonas_pub)):
    routeTableAssoc.append(
        ec2.RouteTableAssociation("devop-rt-assoc-"+str(i),
            subnet_id=zonas_pub[i],
            route_table_id=routeTable.id
            )
    )

## Creacion del SessionManager

policy_ssm = iam.Policy("ssm-policy-ec2-access-"+proyecto,
    path="/",
    description="Mi politica de SSM para acceso a las instancias ec2",
    policy=json.dumps({
        "Version" : "2012-10-17",
        "Statement" : [
        {
            "Effect" : "Allow",
            "Action" : [
            "ssm:UpdateInstanceInformation",
            "ssmmessages:CreateControlChannel",
            "ssmmessages:CreateDataChannel",
            "ssmmessages:OpenControlChannel",
            "ssmmessages:OpenDataChannel"
            ],
            "Resource" : "*"
        },
        {
            "Effect" : "Allow",
            "Action" : [
            "s3:GetEncryptionConfiguration"
            ],
            "Resource" : "*"
        }
        ],
    }),
    tags=values.get("tags")
    )

role_ssm = iam.Role("ssm-role-ec2-access-"+proyecto,
    assume_role_policy=json.dumps({
        "Version" : "2012-10-17",
        "Statement" : [
        {
            "Effect" : "Allow",
            "Principal" : {
            "Service" : "ec2.amazonaws.com"
            },
            "Action" : "sts:AssumeRole"
        }
        ],
    }),
    tags=values.get("tags")
    )

role_policy_ssm = iam.RolePolicyAttachment("attach-ssm",
    role=role_ssm.name,
    policy_arn=policy_ssm.arn)

instance_profile = iam.InstanceProfile("devops-profile-ssm", 
    role=role_ssm.name,
    tags=values.get("tags"))


## Creacion dle SecurityGroup
security_group=ec2.SecurityGroup("devops-sg-"+proyecto,
    description="Grupo de Seguridad para la instancia EC2",
    vpc_id=main.id,
    ingress=[
        ec2.SecurityGroupIngressArgs(
            description="All trafic from vpc",
            from_port=0,
            to_port=0,
            protocol="all",
            cidr_blocks=[values.get("vpc_address")],
        )
    ],
    egress=[
        ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
            ipv6_cidr_blocks=["::/0"],
        )
    ],
    tags=values.get("tags")
    )


## Creacion de la instancia 

linux = ec2.get_ami(most_recent=True,
    filters=[
        ec2.GetAmiFilterArgs(
            name="name",
            values=["amzn2-ami-kernel-*"],
        ),
        ec2.GetAmiFilterArgs(
            name="virtualization-type",
            values=["hvm"],
        ),
    ],
    name_regex="^amzn2-ami-kernel-.*hvm",
    owners=["amazon"])
    
## Instancia en subnet publica 

instancia=ec2.Instance("devops-pub-instance-"+proyecto,
    ami=linux.id,
    instance_type="t2.micro",
    iam_instance_profile=instance_profile.id,
    vpc_security_group_ids=[security_group.id],
    subnet_id=zonas_pub[0].id,
    tags=values.get("tags")
)

## Instancia en subnet privada
instancia=ec2.Instance("devops-priv-instance-"+proyecto,
    ami=linux.id,
    instance_type="t2.micro",
    iam_instance_profile=instance_profile.id,
    vpc_security_group_ids=[security_group.id],
    subnet_id=zonas_priv[0].id,
    tags=values.get("tags")
)