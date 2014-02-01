#!/usr/bin/env python

import argparse
import os
import sys

from os.path import exists, isdir
from subprocess import call


def execute(*args):
    try:
        print args
        retcode = call(args, shell=False)
        if retcode < 0:
            sys.exit(1)
        elif retcode != 0:
            sys.exit(1)
    except OSError:
        sys.exit(1)


class Build():

    def __init__(self):
        self.should_clean = False
        self.configured = False
        self.current_ver = None
        self.current_flavor = 'debug'
        self.products_dir = None
        self.configure_args = []
        self.CXXFLAGS = []
        self.LDFLAGS = []
        self.envars = self.get_env_vars()
        self.parse_cmd_options()

    def get_env_vars(self):
        envvars = {
            'CXX':      'g++',
            'CXXFLAGS': '',
            'LDFLAGS':  '',
        }
        for varname in envvars.keys():
            if varname in os.environ:
                envvars[varname] = os.environ[varname]
                if varname.endswith('FLAGS'):
                    self.__dict__[varname] = str.split(os.environ[varname])
                    envvars[varname] = ''
        return envvars

    def parse_cmd_options(self):
        parser = argparse.ArgumentParser(description="Ledger build wrapper")
        #TODO figure out a nice way to show all possible commands
        parser.add_argument('commands', type=str, nargs='+', default='update')
        parser.add_argument('--debug', action='store_true',
                            help='show debug messages and pass exception')
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='show informational messages')
        parser.add_argument('-q', '--quiet', help='do not show log messages')
        parser.add_argument('--log', metavar='FILE', type=str, dest='logfile',
                            help='append logging data to FILE')
        parser.add_argument('--loglevel', metavar='LEVEL', type=str,
                            help='set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL')
        parser.add_argument('-c', '--config', type=str,
                            help='commands that should be parsed to cmake')
        parser.add_argument('--nogit', action='store_true', help='use git')
        parser.add_argument('--make', type=str, help='arguments that you want to give to make')
        self.args = parser.parse_args()

    def run(self):
        "process all commands given"
        commands = self.args.commands
        print commands

        # work of all commands
        if 'update' in commands:
            self.update()
        if 'make' in commands:
            self.make()

    def update(self):
        self.git('pull')
        self.git('submodule update --init')
        self.make()

    def git(self, command):
        """execute git command if we are in the root dir. The command should
           be given as one string
        """
        if exists('.git') and isdir('.git') and not self.args.nogit:
            # split up the command string for subprocess.call
            execute('git', *command.split(' '))

    def make(self):
        make_args = self.args.commands

        if self.args.verbose:
            make_args.append('VERBOSE=1')
        self.config()

        command = 'make ' + self.args.make
        execute(*command.split(' '))

    def config(self):
        if self.configured:
            return
        self.configured = True
#         environ, conf_args = self.config_env()
        print 'run cmake'
        command = 'cmake .'
        execute(*command.split(' '))

    def config_env(self):
        pass


if __name__ == '__main__':
    build = Build()
    build.run()
