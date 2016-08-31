assh - select your servers from aws with ncurses and then ssh easily - or do something else with them.

[![asciicast](https://asciinema.org/a/2ga28o9gnondowm60ol7iad69.png)](https://asciinema.org/a/2ga28o9gnondowm60ol7iad69)

How
==========================
assh brings a list of servers from your AWS account. Search, move, Hit enter to select one,
then ssh (or whatever you want) to them.

Its extendible, so you can add some other commands - use it with fabric, ansible, ssh etc.


Why
==========================
Because servers come and go, and i started hating the questions "Do we have 2 appservers in X project or 3 ? ", "was it app4.x.project.com or app5.x.project.com".

Installation
=========================
use pip to install

    pip install assh

then create a python file in your ~/.assh directory with somename

    mkdir ~/.assh
    vim ~/.assh/project.py

add your AWS account info

    AWS_ACCESS_KEY_ID = 'XXXXX'
    AWS_SECRET_ACCESS_KEY = 'YYYY'
    AWS_SECURITY_TOKEN = None # OPTIONAL
    AWS_REGION = 'us-east-1'

a region also can be a list eg
    AWS_REGION = 'us-east-2'

and then you can

    assh project ssh

select your fav. server and hit enter.

you can also extend and override commands in project.py file

    def cmd_SSH(self, **kwargs):
        return 'ssh -i ~/.ssh/project.pem ubuntu@{ip}'.format(**kwargs)

your costum command will recieve information about the selected machine

Usage
===========================

using SSH

    assh project ssh

    assh project ssh ssh_user=ubuntu
 
    assh project ssh nat_user=ec2-user
 
    assh project ssh ssh_user=ubuntu nat_user=ec2-user


using SCP

    assh project scp_to src=path/to/local/file to=path/on/remote
    
    assh project scp_from src=remote/path to=local/path

