#!/usr/bin/python3
"""
Palo Panorama boilerplate
"""
import requests
import urllib3
import json
import xml.etree.ElementTree as xml

host = ""
key  = ""


# Class definition
class Panorama:
    """
    Panorama Class
    """

    # Class constructor
    def __init__(self, host:str, key:str, verify:bool=False, port:int=443):
        """
        Args:
            host (str): IP or hostname (without https://)
            key (str): API key
            verify (bool): enable / disable certificate check
            port (int): TCP port number (defaults to 443)
        """
        # Base properties
        self.verify = verify
        self.key = key
        self.base_url = "https://" + host + ":" + str(port) + "/api/?type=op&key=" + key + "&cmd="
        self.session = requests.Session()
        # SSL verify
        if not verify:
            urllib3.disable_warnings()
        # HTTP headers
        self.headers = {
            "Content-Type":  "application/xml; charset=utf-8",
            "cache-control": "no-cache",
        }
        # Requests args
        self.kwargs = {"verify": verify, "headers": self.headers}

    # Private method
    def __get(self,command:str):
        """
        Generic GET request
        Returns:
            str: response body
        """
        try:
            response = self.session.get(self.base_url + command, **self.kwargs)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'ConnectionError: {e}') 
        return response.text if response.status_code == 200 else None

    # Public method
    def getDevices(self):
        """
        Get devices
        Returns:
            dict: Device inventory
        """
        command = "<show><devices><connected></connected></devices></show>"
        raw_xml = self.__get(command)
        if raw_xml:
            result = []
            for device in xml.fromstring(raw_xml).findall('./result/devices/entry'):
                #print(xml.tostring(device, encoding='utf8').decode('utf8'))
                element = {
                    "hostname"       : device.find('hostname').text.lower(),
                    "ip_address"     : device.find('ip-address').text,
                    "status"         : device.find('operational-mode').text,
                    "family"         : device.find('family').text,
                    "model"          : device.find('model').text,
                    "serial"         : device.find('serial').text,
                }
                result.append(element)
            return result
        return None

# Run
if __name__ == "__main__":
    # Instantiate class
    session = Panorama(host, key)
    # Get inventory
    devices = session.getDevices()
    print(json.dumps(devices)) if devices else print("ERROR")



