#-*- coding: utf-8 -*-

import boto3

import imp
import subprocess

from hst.hst import main
import os
import sys
if os.name != 'posix':
    sys.exit('platform not supported')
import logging
import os
import argparse
from hst.hst import Picker, QuitException


import locale
locale.setlocale(locale.LC_ALL,"")

logger = logging.getLogger(__name__)

from .client import AWSCli
from .interface import SimpleLineLoader, BasePicker

class AsshPicker(BasePicker):


    def key_ENTER(self):
        line = self.pick_line()
        self.no_enter_yet = False
        logger.debug("selected_lineno: %s", line)

        args = self.get_data_from_line(line)

        logger.debug("selected line: %s", line)

        if self.args.rest:
            for arg in self.args.rest:
                key, value = arg.split('=')
                args[key] = value

        if self.args.command:
            fn = self.get_cmd_fn(self.args.command)
            line = fn(**args)

        self.write_output(line)

        raise QuitException()


def assh():
    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--out", type=str,
                    help="output to file")

    parser.add_argument("-F", "--filter-tag",
                        nargs='+',
                    help="filter by tags eg: --filter-tag=Name:app1")

    parser.add_argument('-N', '--filter-name', help="filter by tag Name")

    parser.add_argument("-d", "--debug",
                    help="debug mode - shows scores etc.")

    parser.add_argument("-i", "--input",
                    help="input file")

    parser.add_argument("-e", "--eval",
                    help="evaluate command output")

    parser.add_argument("-p", "--pipe-out", action='store_true',
                    help="just echo the selected command, useful for pipe out")

    parser.add_argument("-I", "--separator",
                        default=',',
                        help="seperator in for multiple selection - ie. to join selected lines with ; etc.")

    parser.add_argument("-r", "--replace",
                        default=' ',
                        help="replace with this in eval string. ie. hst -r '__' --eval='cd __ && ls'")

    parser.add_argument("-l", "--logfile",
                        default='assh.log',
                        help="where to put log file in debug mode")

    parser.add_argument("account", type=str,
                    help="aws account")
    #
    parser.add_argument("command", type=str, nargs='?',
                    help="command - eg. ssh, fab")

    parser.add_argument('rest', nargs=argparse.REMAINDER)


    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        hdlr = logging.FileHandler(args.logfile)
        logger.addHandler(hdlr)
    else:
        logger.setLevel(logging.CRITICAL)

    settings = imp.load_source('settings', '%s/.assh/%s.py' % (os.path.expanduser('~'), args.account))

    AsshPicker.settings = settings

    tags = {}
    if args.filter_tag:
        for n in args.filter_tag:
            k, v = n.split(':')
            tags[k] = v

    if args.filter_name:
        tags['Name'] = args.filter_name

    client = AWSCli(settings.AWS_REGION,
                    settings.AWS_ACCESS_KEY_ID,
                    settings.AWS_SECRET_ACCESS_KEY,
                    settings.AWS_SECURITY_TOKEN)

    AsshPicker.client = client


    loader = SimpleLineLoader(client=client,
                              tags=tags)

    lines = loader.load()

    if args.command=='list':
        for n in lines:
            print(n)
        return

    main(args,
         picker_cls=AsshPicker,
         loader=loader)

if __name__ == '__main__':
    assh()
