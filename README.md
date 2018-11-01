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

* python
* Qumulo API python library

From a terminal window, run
```
pip install -r requirements.txt
```

It is recommended to use a virtual environment for python support and 
not change or depend upon the system version of python.  A backgrounder
on python virtual environments can be found here:

https://community.qumulo.com/qumulo/topics/virtual-environments-when-using-qumulo-rest-api


## Usage

    python ./qdu.py -s [-k] [--time] [path]
    
where

    -k display size in KB

    --time works like du --time (show most-recent change datetime for 
    contents of specified path.  For now we only support an implicit
    --time-style=long-iso
    
    [path] is a file path or mount point for a Qumulo cluster


Example:
   
    python ./qdu.py -s -k --user admin --pass password /mnt/cluster/directory

