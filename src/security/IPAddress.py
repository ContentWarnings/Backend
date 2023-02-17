# References
# https://stackoverflow.com/questions/68231936/how-can-i-get-headers-or-a-specific-header-from-my-backend-api

from fastapi import Request


class IPAddress:
    @staticmethod
    def get_ip_address(request: Request) -> str:
        """
        Returns IP address, given a request object
        """
        # for logging
        print(request.headers)

        priority_ip = "cf-connecting-ip"

        if priority_ip in request.headers.keys():
            return request.headers.get(priority_ip)

        return request.client.host
