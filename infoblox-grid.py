#!/usr/bin/python3
"""
Infoblox boilerplate
"""
import base64
import requests
import urllib3
import json

host     = ""
username = ""
password = ""

# Class definition
class Infoblox:
    """
    Infoblox Class
    """

    # Class constructor
    def __init__(self, host:str, username:str , password:str , verify:bool=False, port:int=443, version:str="2.12"):
        """
        Args:
            host (str): IP or hostname (without https://)
            username (str): Username
            password (str): Password
            verify (bool): enable / disable certificate check
            port (int): TCP port number (defaults to 443)
            version (str): API version (defaults to 2.12)
        """
        # Base properties
        self.username = username
        self.password = password
        self.creds = ":".join([self.username, self.password])
        self.encoded_auth = base64.b64encode(self.creds.encode("utf-8"))
        self.base_url = 'https://' + host + ":" + str(port) + "/wapi/v" + str(version) + "/"
        self.session = requests.Session()
        # SSL verify
        if not verify:
            urllib3.disable_warnings()
        # HTTP headers
        self.headers = {
            "Authorization": " ".join(["Basic", self.encoded_auth.decode("utf-8")]),
            "cache-control": "no-cache",
        }
        # Requests args
        self.kwargs = {"verify": verify, "headers": self.headers}

    # Private method
    def __get(self,object:str):
        """
        Generic GET request
        Returns:
            str: response body
        """
        try:
            response = self.session.get(self.base_url + object, **self.kwargs)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'ConnectionError: {e}')        
        return response.text if response.status_code == 200 else None

    # Public method
    def getDevices(self):
        """
        Get Grid Members
        Returns:
            dict: Grid member list
        """
        members = self.__get('member')
        return json.loads(members) if members else None

# Run
if __name__ == "__main__":
    # Instantiate class
    session = Infoblox(host, username, password)
    # Get Grid members
    members = session.getDevices()
    print(json.dumps(members)) if members else print("ERROR")
