#!/usr/bin/python3
"""
vManage boilerplate - async version
"""
import asyncio
import httpx
import json

# Max concurrent tasks
concurrency = 10

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
        # SSL verify
        self.verify = verify
        # Login
        self.connected = self.__login(username,password)
        if self.connected:
            self.session = httpx.AsyncClient(verify=verify)

    # Login method
    def __login(self, username:str, password:str) -> bool:
        """
        Authenticates to vManage and update session
        """
        # Create HTTPX client
        client = httpx.Client(verify=self.verify)
        # Submit login form
        headers = { "Content-Type": "application/x-www-form-urlencoded" }
        data = { "j_username": f"{username}", "j_password": f"{password}" }
        try:
            response = client.post(f"{self.base_url}/j_security_check", data=data, headers=headers)
        except httpx.HTTPError as e:
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
            # Get CSRF token
            try:
                response = client.get(f"{self.base_url}/dataservice/client/token", headers=self.headers)
            except httpx.HTTPError as e:
                raise ConnectionError(f'ConnectionError: {e}')    
            if response.status_code == 200:
                # Add CSRF header
                self.headers["X-XSRF-TOKEN"] = response.text
                # Update base path
                self.base_url = self.base_url + "/dataservice/"
                return True
        # Fail by default
        return False

    # Private method
    async def __get(self,path:str) -> str:
        """
        Generic GET request
        Returns:
            str: response body
        """
        if not self.connected:
            return None
        try:
            response = await self.session.get(f"{self.base_url}{path}", headers=self.headers)
        except httpx.HTTPError as e:
            raise ConnectionError(f'ConnectionError: {e}')
        return response.text if response.status_code == 200 else None

    # Public method
    async def get(self,endpoint:str) -> dict:
        response = await self.__get(endpoint)
        return json.loads(response)['data'] if response else None

# Concurrent GET function
async def get(tasks) -> list[any]:
    semaphore = asyncio.Semaphore(concurrency)
    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*[sem_task(task) for task in tasks])

# Run
if __name__ == "__main__":

    # For Windows only:
    import platform
    if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Instantiate class
    session = Vmanage(host, username, password)

    # Get devices and device groups concurrently
    tasks = [session.get("device"), session.get("group")]
    (devices,groups) = asyncio.run( get(tasks) )

    # Print results
    if devices and groups:
        for group in groups:
            print(f'- Members of group {group["groupName"]}:')
            for device in devices:
                if group["groupName"] in device["device-groups"]:
                    print(f'\t- {device["host-name"]} ({device["version"]})')
    else:
        print("ERROR")
