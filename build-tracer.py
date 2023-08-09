# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
    Tracer tool using git.
    
    This script will generate a tracer branch, and commit any change onto it on each execution.
    
    The intention of this script is to track any change made to the project, user can insert this
    script into the build process to track the change between each build.
"""

import os.path as path
import subprocess
import argparse
import sys
import os


def change_working_directory(cwd, dry_run=False, verbose=False):
    """Change working directory.

    Args:
        cwd (str): The working directory to change to.
        dry_run (bool, optional): is dry run. Defaults to False.
        verbose (bool, optional): is verbose mode. Defaults to False.
    """
    if dry_run or verbose:
        print(f"cd {cwd}")

    if not dry_run:
        os.chdir(cwd)


def run_command(cmd: str, dry_run=False, verbose=False):
    """Run a command and return the output.

    Args:
        cmd (str): the command to run.
        dry_run (bool, optional): is dry run. Defaults to False.
        verbose (bool, optional): is verbose mode. Defaults to False.

    Returns:
        (int, str): return code and stdout. 
    """

    if isinstance(cmd, list):
        cmd = ' '.join(cmd)

    if dry_run or verbose:
        print(cmd)

    # wait for command to finish with timeout
    if not dry_run:
        try:
            process = subprocess.run(cmd,
                                     shell=True,
                                     check=True,
                                     stdout=subprocess.PIPE,
                                     timeout=10,
                                     )

            return_code = process.returncode
            stdout = process.stdout.decode('utf-8')
            return return_code, stdout

        except subprocess.TimeoutExpired as ex:
            return (-1, ex.stdout.decode('utf-8'))
        except subprocess.CalledProcessError as ex:
            return (ex.returncode, ex.stdout.decode('utf-8'))
        except Exception as ex:
            return (-1, "")
    else:
        return 0, ""


def get_cli_args_parser():
    """Get the command line arguments parser.
    """
    parser = argparse.ArgumentParser(prog="build-tracer.py",
                                     description=__doc__,)

    parser.add_argument('-b', '--branch', dest='branch', default='master')

    parser.add_argument('-t', '--tracer-name',
                        dest='tracer_name', default='build-tracer')

    parser.add_argument('-m', '--message', dest='message',
                        default='build-tracer')

    parser.add_argument('-n', '--dry-run', dest='dry_run', default=False)

    parser.add_argument('-v', '--verbose', dest='verbose', default=False)

    parser.add_argument('-C', '--cwd', dest='cwd', default='.')

    return parser


def create_tracer_branch(branch_name, dry_run=False, verbose=False):
    """Create a tracer branch.

    this function will check if the tracer branch exists, if not, it will create one.

    Args:
        branch_name (_type_): the name of the tracer branch.
        dry_run (bool, optional): is dry run. Defaults to False.
        verbose (bool, optional): is verbose mode. Defaults to False.
    """

    # check if tracer branch exists
    ret, tracer_branch = run_command(f'git branch --list {branch_name}')
    if ret != 0:
        print("command failed: ", tracer_branch, file=sys.stderr)
    if tracer_branch.strip() == '':
        # create a new branch

        if verbose:
            print("create branch: ", tracer_branch)

        ret, output = run_command(
            f'git branch {branch_name}', verbose=verbose, dry_run=dry_run)
        if ret != 0:
            print("command failed: ", output, file=sys.stderr)


def main():
    """The main function.
    """

    # save current working directory
    cwd = os.getcwd()
    cwd = path.abspath(cwd)

    try:
        # parse arguments

        parser = get_cli_args_parser()
        args = parser.parse_args()
        os.chdir(path.abspath(args.cwd))

        # check if git in installed
        ret, git_version = run_command('git --version')
        if ret != 0:
            print("git is not installed.", file=sys.stderr)
            sys.exit(1)
        if args.verbose:
            print("find git: ", git_version)

        # check if arg is a valid git repo
        ret, git_repo = run_command('git rev-parse --is-inside-work-tree')
        if ret != 0 and git_repo.strip() != 'true':
            print("not a valid git repo.", file=sys.stderr)
            sys.exit(1)

        # get the base commit-id
        ret, base_commit = run_command('git rev-parse HEAD')
        if ret != 0:
            print("failed to get base commit-id.", file=sys.stderr)
            sys.exit(1)

    finally:
        # restore working directory
        os.chdir(cwd)


if __name__ == '__main__':
    main()
