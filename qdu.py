#!/usr/bin/env python3
# Copyright (c) 2015 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# Import python libraries
import getopt
from math import log
import argparse
import os
import sys
import time
import re
import subprocess
import socket

from dateutil import parser, tz
from typing import Sequence

# Import Qumulo REST libraries
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.lib.request
import qumulo.rest


def parse_args(args: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Calculates the disk usage of a Qumulo cluster.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'files',
        metavar='file',
        type=str,
        nargs='+',
        help='Display an entry for each specified file. (Equivalent to `du -d 0`)',
    )
    parser.add_argument(
        '-k',
        '--in-kibibytes',
        help='Display block counts in 1024-byte (1KiB) blocks.',
        action='store_true'
    )
    parser.add_argument(
        '-u',
        '--user',
        type=str,
        help='Use the given username for authentication.',
        default='admin'
    )
    parser.add_argument(
        '-p',
        '--password',
        type=str,
        help='Use the given password for authentication.',
        default='admin'
    )
    parser.add_argument(
        '-P',
        '--port',
        type=int,
        help='Use the given port to contact the API server for authentication.',
        default=8000
    )

    return parser.parse_args(args)


#### Subroutines
def login(host, user, passwd, port):
    '''Obtain credentials from the REST server'''
    connection = None
    credentials = None

    try:
        # Create a connection to the REST server
        connection = qumulo.lib.request.Connection(host, int(port))

        if credentials is None:
            # Provide username and password to retreive authentication tokens
            # used by the credentials object
            login_results, _ = qumulo.rest.auth.login(
                    connection, None, user, passwd)

            # Create the credentials object which will be used for
            # authenticating rest calls
            credentials = (qumulo.lib.auth.Credentials
                           .from_login_response)(login_results)
    except Exception as excpt:
        print("Error connecting to the REST server: %s" % excpt)
        print(__doc__)
        sys.exit(1)

    return (connection, credentials)

def pingserver(server):
    ping = subprocess.Popen(
        ["ping", "-c", "1", server],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
    )

    out, error = ping.communicate()
    if error:
        print(error.replace("ping: ","ERROR: "))
        sys.exit()

def checkfs(file, port):
    df = subprocess.Popen(["df", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output,error = df.communicate()
    if df.returncode:
        print("ERROR:",error.decode('utf-8'))
        sys.exit()
    output = output.decode('utf-8').split("\n")[1]
    columns = re.split("\s+", output)
    if ':' in columns[0]:
        host,pathmounted = columns[0].split(":")
        mountpoint = columns[-1]
        if mountpoint.startswith("/private"): mountpoint = mountpoint[8:]
        if portisopen(host, port):
            return(True,host,mountpoint,pathmounted)
        else:
            return(False,None,None,None)
    else:
        return(False,None,None,None)

def portisopen(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host,int(port)))
    if result == 0:
        return True
    else:
        return False

### make a nicely-formaatted size string
def sizeof_fmt(num):
    """Human friendly file size"""

    unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])

    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'


def process_folder(connection, credentials, path, k, show_time):

    data = qumulo.rest.fs.read_dir_aggregates(connection, credentials, path)

    size = int(data[0]['total_data'])
    total_files = int(data[0]['total_files'])

    if k:
        size = str(size/1024)
    else:
        size = sizeof_fmt(size)

    print(size + "\t" + path)


### Main subroutine
def main():
    args = parse_args(sys.argv)

    if args.files:
        for file in args.files:
            isqumulo, host, mountpoint, pathmounted = checkfs(file, args.port)
            if isqumulo:
                (connection, credentials) = login(host, args.user, args.passwd, args.port)
                path = os.path.abspath(file)
                if path == ".":
                    path = os.getcwd() + "/"
                path = path.replace(mountpoint, '')
                process_folder(connection, credentials, path, args.k, args.time)
            else:
                print("This is not a path mounted against a Qumulo cluster.")
    else:
        print("So far I've only implemented the -s -k switches... sorry...")
        sys.exit()

# Main
if __name__ == '__main__':
    main()
