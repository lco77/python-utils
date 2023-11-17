#!/usr/bin/python3
"""
vManage boilerplate
"""
import requests
import urllib3
import json

host     = ""
username = ""
password = ""

# Class definition
class Vmanage:
    """
    Vmanage Class
    """

    # Class constructor
    def __init__(self, host:str, username:str , password:str , verify:bool=False, port:int=443):
        """
        Args:
            host (str): IP or hostname (without https://)
            username (str): Username
            password (str): Password
            verify (bool): enable / disable certificate check
            port (int): TCP port number (defaults to 443)
        """
        # Base properties
        self.base_url = 'https://' + host + ":" + str(port)
        self.session = requests.Session()
        # SSL verify
        self.verify = verify
        if not verify:
            urllib3.disable_warnings()
        # Login
        self.connected = self.__login(username,password)

    # Login method
    def __login(self, username:str, password:str):
        """
        Authenticates to vManage and update session
        """
        # Submit login form
        headers = { "Content-Type": "application/x-www-form-urlencoded" }
        data = { "j_username": f"{username}", "j_password": f"{password}" }
        try:
            response = self.session.post(f"{self.base_url}/j_security_check", data=data, headers=headers, verify=self.verify)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'ConnectionError: {e}')
        # Login OK when response code is 200 AND content is not HTML
        if response.status_code == 200 and not response.text.startswith('<html>'):
            # Get session cookie
            cookie = response.headers.get('Set-Cookie').split(";")[0]
            # Set headers
            self.headers = {
                "Content-Type": "application/json",
                "Cookie" : cookie
            }
            self.kwargs = {"verify": self.verify, "headers": self.headers}
            # Get CSRF token
            try:
                response = self.session.get(f"{self.base_url}/dataservice/client/token", **self.kwargs)
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f'ConnectionError: {e}')    
            if response.status_code == 200:
                # Add CSRF header
                self.headers["X-XSRF-TOKEN"] = response.text
                self.kwargs = {"verify": self.verify, "headers": self.headers}
                # Update base path
                self.base_url = self.base_url + "/dataservice/"
                return True
        # Fail by default
        return False

    # Private method
    def __get(self,path:str):
        """
        Generic GET request
        Returns:
            str: response body
        """
        if not self.connected:
            return None
        try:
            response = self.session.get(f"{self.base_url}{path}", **self.kwargs)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'ConnectionError: {e}')
        return response.text if response.status_code == 200 else None

    # Public method
    def getDevices(self):
        """
        Get devices
        Returns:
            dict: Device list
        """
        devices = self.__get('device')
        return json.loads(devices)['data'] if devices else None

# Run
if __name__ == "__main__":
    # Instantiate class
    session = Vmanage(host, username, password)
    # Get devices
    devices = session.getDevices()
    print(json.dumps(devices)) if devices else print("ERROR")
