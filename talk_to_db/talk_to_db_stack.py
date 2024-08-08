# Import necessary modules from aws_cdk and constructs
from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    SecretValue
)
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as rds
from constructs import Construct

# Define a custom stack class TalkToDbStack that extends Stack
class TalkToDbStack(Stack):

    # Constructor method for TalkToDbStack
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        # Call the parent class constructor
        super().__init__(scope, id, **kwargs)

        # Create a VPC with two availability zones
        vpc = ec2.Vpc(self, "TalkToDbVpc", max_azs=2)

        # Create a security group within the VPC
        security_group = ec2.SecurityGroup(
            self, "TalkToDbSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )

        # Allow inbound traffic on port 3306 (MySQL default port) from any IPv4 address
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(3306),
            description="Allow inbound traffic on port 3306 from anywhere"
        )

        # Create an RDS database instance within the VPC with specified configurations
        db_instance = rds.DatabaseInstance(
            self, "TalkToDbDatabase",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_32  # Use a supported MySQL version
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            credentials=rds.Credentials.from_password(
                username="admin",
                password=SecretValue.unsafe_plain_text("your-custom-password")  # Replace with your own password
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            port=3306,
            allocated_storage=80,
            multi_az=False,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False,
            publicly_accessible=True,
            security_groups=[security_group]
        )

        # Output the necessary information for connection
        CfnOutput(
            self, "DBInstanceEndpoint",
            value=db_instance.db_instance_endpoint_address,
            description="The endpoint address of the RDS instance"
        )

        CfnOutput(
            self, "DBInstancePort",
            value=str(db_instance.db_instance_endpoint_port),
            description="The port number of the RDS instance"
        )

        CfnOutput(
            self, "DBInstanceUsername",
            value="admin",  # The username for the RDS instance
            description="The username for the RDS instance"
        )
