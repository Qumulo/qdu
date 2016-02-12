#!/usr/bin/env python
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

'''
=== Options:

 -s                                 Display an entry for each specified file.  (Equivalent to -d 0)
 -k                                 Display block counts in 1024-byte (1-Kbyte) blocks.
 --time                             Equivalent to du --time --time-style=long-iso

[-u | --user] username              Use 'username' for authentication
                                        (defaults to 'admin')
[-p | --passwd] password            Use 'password' for authentication
                                        (defaults to 'admin')
[-P | --port] number                Use 'number' for the API server port
                                        (defaults to 8000)

-h | --help                         Print out the script usage/help


'''

# Import python libraries
import getopt
from math import log
import os
import sys
import time
import re
import subprocess
import socket

from dateutil import parser, tz

# Import Qumulo REST libraries
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.lib.request
import qumulo.rest


#### Classes
class Args(object):
    '''
    This class defines a dictionary of script variables. On creation,
    it parses the command line for user values, and returns a dictionary.
    '''

    def __init__(self, argv):
        self.port = 8000
        self.user = 'admin'
        self.passwd = 'admin'
        self.files = ['.']
        self.s = None
        self.k = None
        self.time = True

        opts = {}
        try:
            opts, _arg = getopt.getopt(argv[1:], "kshp:P:u:",
                                    [
                                     "help",
                                     "user=",
                                     "pass=",
                                     "port=",
                                    ])
        except getopt.GetoptError, msg:
            print msg
            print __doc__
            try:
                # os.EX_USAGE exists only on Unix systems
                sys.exit(os.EX_USAGE)
            except:
                sys.exit(1)

        if _arg: self.files = _arg

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print __doc__
                sys.exit(0)
            elif opt in ("-s"):
                self.s = True  
            elif opt in ("-k"):
                self.k = True
            elif top in ("--time"):
                self.time = True
            elif opt in ("--port", "-P"):
                self.port = arg
            elif opt in ("--user", "-u"):
                self.user = arg
            elif opt in ("--pass", "-p"):
                self.passwd = arg
            else:
                try:
                    # os.EX_USAGE exists only on Unix systems
                    sys.exit(os.EX_USAGE)
                except:
                    sys.exit(1)

#### Subroutines
def login(host, user, passwd, port):
    '''Obtain credentials from the REST server'''
    connection = None
    credentials = qumulo.lib.auth.get_credentials(
                    qumulo.lib.auth.credential_store_filename())

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
    except Exception, excpt:
        print "Error connecting to the REST server: %s" % excpt
        print __doc__
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
        print error.replace("ping: ","ERROR: ")
        sys.exit()

def checkfs(file, port):
    df = subprocess.Popen(["df", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output,error = df.communicate()
    if df.returncode: 
        print "ERROR:",error
        sys.exit()
    output = output.split("\n")[1]
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

    size = int(data[0]['total_capacity'])
    max_change_time = data[0]['max_change_time']
    utc = parser.parse(max_change_time)

    # convert datetime to local timezone
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = utc.replace(tzinfo=from_zone)
    most_recent_change = utc.astimezone(to_zone)


    if show_time:
        response = qumulo.rest.fs.read_entire_directory(connection, credentials,
                                             page_size=5000, path=path)
        for r in response:
            for entry in r.data['files']:
                if entry['type'] == 'FS_FILE_TYPE_DIRECTORY':
                    new_path = path + "/" + entry['name']
                    process_folder(connection, credentials, new_path, k, show_time)

    if k:
        size = str(size/1024)
    else:
        size = sizeof_fmt(size)

    print size + "\t" + most_recent_change.strftime("%Y-%m-%d %H:%M") + "\t" + path

### Main subroutine
def main():
    
    args = Args(sys.argv)

    if args.s:
        for file in args.files:
            isqumulo, host, mountpoint, pathmounted = checkfs(file, args.port)

            if isqumulo:
                (connection, credentials) = login(host, args.user, args.passwd, args.port)
                qefspath = file.replace(mountpoint,"")

                if pathmounted is not "/": qefspath = pathmounted+qefspath

                process_folder(connection, credentials, qefspath, args.k, args.time)

            else:
                if args.k:
                    du = subprocess.Popen(["du", "-s", "-k", "--time", "--time-style=long-iso", file], stdout=subprocess.PIPE)
                    print(du.communicate()[0]),
                else:
                    du = subprocess.Popen(["du", "-s", "--time", "--time-style=long-iso", file], stdout=subprocess.PIPE)
                    print(du.communicate()[0]),
    else:
        print "So far I've only implemented the -s -k switches... sorry..."
        sys.exit()

# Main
if __name__ == '__main__':
    main()
