# Qumulo qdu (Qumulo du command)

Licensed under the Educational Community License, Version 2.0 (ECL-2.0) (the "License");
you may not use this file except in compliance with the License.  Please refer to LICENSE
file as part of this project for details.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.

## Requirements

* python 3.4 (or above)
* Qumulo API python library

From a terminal window, run
```
pip3 install -r requirements.txt
```

It is recommended to use a virtual environment for python support and
not change or depend upon the system version of python.  A backgrounder
on python virtual environments can be found here:

https://community.qumulo.com/qumulo/topics/virtual-environments-when-using-qumulo-rest-api


## Usage
```
usage: qdu.py [-h] [-k] [-u USER] [-p PASSWORD] [-P PORT] file [file ...]

Calculates the disk usage of files on a Qumulo cluster.

positional arguments:
  file                  Display an entry for each specified file. (Equivalent
                        to `du -d 0`)

optional arguments:
  -h, --help            show this help message and exit
  -k, --in-kibibytes    Display block counts in 1024-byte (1KiB) blocks.
                        (default: False)
  -u USER, --user USER  Use the given username for authentication.
                        (default: admin)
  -p PASSWORD, --password PASSWORD
                        Use the given password for authentication.
                        (default: admin)
  -P PORT, --port PORT  Use the given port to contact the API server for
                        authentication.
                        (default: 8000)
```
