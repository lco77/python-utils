# Python Utils

Ready to use boilerplates to interact with various APIs.

Each boilerplate should meet the following requirements:
- minimal set of external dependencies
- a base class to instantiate a session to a target system
- one or more private methods for low-level API interactions
- one or more public methods for high-level API interactions
- a simple working example in __main__

# cisco-vmanage.py
Interact with Infoblox GRID master API

Class instantiation:
- Infoblox(hostname, username, password)

Input parameters:
- hostname
- username
- password

# cisco-vmanage-async.py
Interact with Infoblox GRID master API (ASYNC version)

Class instantiation:
- Infoblox(hostname, username, password)

Input parameters:
- hostname
- username
- password

# infoblox-grid.py
Interact with Infoblox GRID master API

Class instantiation:
- Infoblox(hostname, username, password)

Input parameters:
- hostname
- username
- password

External dependencies:
- requests

Public methods:
- getDevices()

# cisco-cspc.py
Interact with Cisco Collector API

Class instantiation:
- CiscoCSPC(hostname, username, password)

Input parameters:
- hostname
- username
- password

External dependencies:
- requests

Public methods:
- getDevices()

# palo-panorama.py
Interact with Palo Alto Panorama API

Class instantiation:
- Panorama(hostname, apikey)

Input parameters:
- hostname
- API key

External dependencies:
- requests

Public methods:
- getDevices()
