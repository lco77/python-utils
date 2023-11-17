#!/usr/bin/python3
"""
Cisco Collector boilerplate
"""
import base64
import requests
import urllib3
import json
import xml.etree.ElementTree as xml

host     = ""
username = ""
password = ""

# Class definition
class CiscoCSPC:
    """
    CiscoCSPC Class
    """

    # Class constructor
    def __init__(self, host:str, username:str , password:str , verify:bool=False, port:int=8001):
        """
        Args:
            host (str): IP or hostname (without https://)
            username (str): Username
            password (str): Password
            verify (bool): enable / disable certificate check
            port (int): TCP port number (defaults to 443)
        """
        # Base properties
        self.verify = verify
        self.username = username
        self.password = password
        self.creds = ":".join([self.username, self.password])
        self.encoded_auth = base64.b64encode(self.creds.encode("utf-8"))
        self.base_url = 'https://' + host + ":" + str(port) + "/cspc/xml"
        self.session = requests.Session()
        # SSL verify
        if not verify:
            urllib3.disable_warnings()
        # HTTP headers
        self.headers = {
            "Content-Type":  "application/xml; charset=utf-8",
            "Authorization": " ".join(["Basic", self.encoded_auth.decode("utf-8")]),
            "cache-control": "no-cache",
        }
        # Requests args
        self.kwargs = {"verify": verify, "headers": self.headers}

    # Private method
    def __post(self,payload:str):
        """
        Generic POST request
        Returns:
            str: response body
        """
        try:
            response = self.session.post(self.base_url, data=payload, **self.kwargs)
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
        payload = '''<Request xmlns="http://www.parinetworks.com/api/schemas/1.1" requestId="">
                        <Manage>
                            <Get operationId="1">
                                <DeviceList all="true" />
                            </Get>
                        </Manage>
                    </Request>'''
        raw_xml = self.__post(payload)
        if raw_xml:
            result = []
            for device in xml.fromstring(raw_xml).findall('.//Device'):
                #print(xml.tostring(device, encoding='utf8').decode('utf8'))
                element = {
                    "id"             : device.find('Id').text,
                    "hostname"       : device.find('HostName').text.lower() if device.find('Status').text == "Reachable" else None,
                    "ip_address"     : device.find('IPAddress').text,
                    "status"         : device.find('Status').text,
                    "device_family"  : device.find('DeviceFamily').text,
                    "product_family" : device.find('ProductFamily').text,
                    "model"          : device.find('Model').text if device.find('Status').text == "Reachable" else None,
                    "serial"         : device.find('SerialNumber').text if device.find('Status').text == "Reachable" else None,
                }
                result.append(element)
            return result
        return None

# Run
if __name__ == "__main__":
    # Instantiate class
    session = CiscoCSPC(host, username, password)
    # Get inventory
    devices = session.getDevices()
    print(json.dumps(devices)) if devices else print("ERROR")



