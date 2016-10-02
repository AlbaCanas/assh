#-*- coding: utf-8 -*-

import boto3

class AWSCli(object):

    def __init__(self, aws_region, aws_key, aws_secret, aws_security_token=None):
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        self.aws_token = aws_security_token
        self.region = aws_region

        self.session = self.get_region(aws_region)
        self.igw = {}

    def get_region(self, region):
        self.region = region
        session = boto3.Session(aws_access_key_id=self.aws_key,
                                aws_secret_access_key=self.aws_secret,
                                aws_session_token=self.aws_token,
                                region_name=region)
        return session

    def start(self, instance_id):
        instance = self.get_instance(instance_id)
        instance.start()

    def stop(self, instance_id):
        instance = self.get_instance(instance_id)
        instance.stop()

    def get_regions(self):
        return self.session.get_available_regions('ec2')

    def get_instances(self, region, instance_state='running', tags=None):
        """

        :param region:
        :param aws_key:
        :param aws_secret:
        :param tags: is a dictionary, eg: {'Name': 'App1'}
        :return:
        """
        if self.region != region:
            self.session = self.get_region(region)

        ec2 = self.session.resource('ec2')
        filters = []
        if tags:
            for tn, tv in self.tags.iteritems():
                filters.append({'Name': tn, 'Values': [tv]})


        if isinstance(instance_state, list):
            filters.append({'Name': 'instance-state-name', 'Values': instance_state})
        elif instance_state != 'all':
            filters.append({'Name': 'instance-state-name', 'Values': [instance_state]})

        instances = ec2.instances.filter(Filters=filters)
        return instances

    def get_nat(self, instance):
        ec2 = self.session.resource('ec2')
        nat_ip = None
        nat_key = None
        if not instance.public_ip_address:
            if instance.vpc_id not in self.igw:
                for routes in instance.vpc.route_tables.all():
                    for route in routes.routes:
                        if route.instance_id:
                            nat_instance = route.instance_id
                            nat_instance = ec2.Instance(nat_instance)
                            nat_ip = nat_instance.public_ip_address
                            nat_key = nat_instance.key_name
                            self.igw[instance.vpc_id] = (nat_ip, nat_key)
                            break
            else:
                nat_ip, nat_key = self.igw[instance.vpc_id]
        return nat_ip, nat_key

    def get_instance(self, instance_id):
        ec2 = self.session.resource('ec2')
        instance = ec2.Instance(instance_id)
        return instance
