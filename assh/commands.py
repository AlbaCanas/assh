#-*- coding: utf-8 -*-

import subprocess


def cmd_SSH(self, ssh_user='ec2-user', nat_user='ec2-user', **kwargs):
    if 'nat_ip' in kwargs and kwargs['nat_ip'] not in [None, 'None']:
        command = 'ssh -o ProxyCommand="ssh -W %h:%p -i ~/.ssh/{nat_key}.pem {nat_user}@{nat_ip}" -i ~/.ssh/{key_name}.pem {ssh_user}@{ip}'
    else:
        command = 'ssh -i ~/.ssh/{key_name}.pem {ssh_user}@{ip}'
    return command.format(ssh_user=ssh_user, nat_user=nat_user, **kwargs)


def cmd_PROXY_HTTP(self, **kwargs):
    return 'ssh -N -L 8000:{ip}:8000 -i ~/.ssh/{nat_key}.pem ec2-user@{nat_ip}'.format(**kwargs)


def cmd_SCP_TO(self, ssh_user='ec2-user', nat_user='ec2-user', **kwargs):
    if 'nat_ip' in kwargs and kwargs['nat_ip'] not in [None, 'None']:
        command = 'scp -o ProxyCommand="ssh -W %h:%p -i ~/.ssh/{nat_key}.pem {nat_user}@{nat_ip}" -i ~/.ssh/{key_name}.pem {src} {ssh_user}@{ip}:{to}'
    else:
        command = 'scp -i ~/.ssh/{key_name}.pem {src} {ssh_user}@{ip}:{to}'

    return command.format(ssh_user=ssh_user, nat_user=nat_user, **kwargs)


def cmd_SCP_FROM(self, ssh_user='ec2-user', nat_user='ec2-user', **kwargs):
    if 'nat_ip' in kwargs and kwargs['nat_ip'] not in [None, 'None']:
        command = 'scp -o ProxyCommand="ssh -W %h:%p -i ~/.ssh/{nat_key}.pem {nat_user}@{nat_ip}" -i ~/.ssh/{key_name}.pem {ssh_user}@{ip}:{src} {to}'
    else:
        command = 'scp -i ~/.ssh/{key_name}.pem {ssh_user}@{ip}:{src} {to}'

    return command.format(ssh_user=ssh_user, nat_user=nat_user, **kwargs)


#def cmd_FAB(self, line):
#    rest = subprocess.list2cmdline(self.args.rest)
#    return 'fab -H %s %s' % (line, rest)



def cmd_INFO(self, **kwargs):
    instance_info = """
id
groups - A list of Group objects representing the security groups associated with the instance.
public_dns_name - The public dns name of the instance.
private_dns_name - The private dns name of the instance.
state - The string representation of the instance’s current state.
state_code - An integer representation of the instance’s current state.
previous_state - The string representation of the instance’s previous state.
previous_state_code - An integer representation of the instance’s current state.
key_name - The name of the SSH key associated with the instance.
instance_type - The type of instance (e.g. m1.small).
launch_time - The time the instance was launched.
image_id - The ID of the AMI used to launch this instance.
placement - The availability zone in which the instance is running.
placement_group - The name of the placement group the instance is in (for cluster compute instances).
placement_tenancy - The tenancy of the instance, if the instance is running within a VPC. An instance with a tenancy of dedicated runs on a single-tenant hardware.
kernel - The kernel associated with the instance.
ramdisk - The ramdisk associated with the instance.
architecture - The architecture of the image (i386|x86_64).
hypervisor - The hypervisor used.
virtualization_type - The type of virtualization used.
product_codes - A list of product codes associated with this instance.
ami_launch_index - This instances position within it’s launch group.
monitored - A boolean indicating whether monitoring is enabled or not.
monitoring_state - A string value that contains the actual value of the monitoring element returned by EC2.
spot_instance_request_id - The ID of the spot instance request if this is a spot instance.
subnet_id - The VPC Subnet ID, if running in VPC.
vpc_id - The VPC ID, if running in VPC.
private_ip_address - The private IP address of the instance.
ip_address - The public IP address of the instance.
platform - Platform of the instance (e.g. Windows)
root_device_name - The name of the root device.
root_device_type - The root device type (ebs|instance-store).
block_device_mapping - The Block Device Mapping for the instance.
state_reason - The reason for the most recent state transition.
interfaces - List of Elastic Network Interfaces associated with this instance.
ebs_optimized - Whether instance is using optimized EBS volumes or not.
instance_profile - A Python dict containing the instance profile id and arn associated with this instance.
    """

    ret = []
    our_instance = self.get_instance_by_public_ip(kwargs['public_ip'])
    for ln in instance_info.split("\n"):
        if ln:
            kv = ln.split('-')
            k = kv[0].strip()
            if k:
                ret.append(u"%s: %s" % (k.decode('utf8'), getattr(our_instance, k, '')))
    return "%s\n" % '\n'.join(ret)
