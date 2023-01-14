"""
This file implements the C9800 class.

Three methods are available:

-----
set_ap_tag(ap_mac, ap_tag)

This method sets an AP tag to the given AP MAC by calling the REST resource:
/Cisco-IOS-XE-wireless-ap-cfg:ap-cfg-data/ap-tags/ap-tag/

It returns the REST response
-----
get_joined_aps()

This method queries the controller for the list of joined APs using the REST resource:
Cisco-IOS-XE-wireless-access-point-oper:access-point-oper-data/capwap-data

It returns a dictionary of joined APs with the following format:

{
    'FGL2115B015': {'MAC': '00:2c:c8:8b:31:b0'},
    'FGL39392819': {'MAC': '00:2c:c8:8a:11:a0'}
}

"""
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from netaddr import EUI, mac_unix_expanded
import logging


class C9800:
    def __init__(self, ip, user, password):
        self.controller_ip = ip
        self.controller_user = user
        self.controller_password = password
        self.controller_auth = HTTPBasicAuth(user, password)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.ap_list = {}
        self.headers = {
            'Accept': "application/yang-data+json",
            'Content-Type': "application/yang-data+json",
            'cache-control': "no-cache"
        }
        self.baseurl = f"https://{self.controller_ip}/restconf/data/"


    def __execute_REST(self, method, resource, payload=None):
        logging.info(f"Executing method {method} on resource {resource}")
        url = self.baseurl + resource
        response = None
        try:
            response = requests.request(method,
                    url,
                    headers=self.headers,
                    verify=False,
                    auth=self.controller_auth,
                    json=payload)
            response.raise_for_status()
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error: {e}")
        except Exception as err:
            logging.exception(f'Other error occurred: {err}')
        else:
            logging.info(f"Success!")
        return response

    def get_site_tags(self):
        resource = "Cisco-IOS-XE-wireless-site-cfg:site-cfg-data/site-tag-configs/site-tag-config"

        result = self.__execute_REST(method="GET", resource=resource)
        data = result.json()
        logging.info(f"The list of tags is: {data}")
        return data


    def set_site_tag(self, ap_tag):
        logging.info(f"Creating the site tag {ap_tag}")

        resource = "Cisco-IOS-XE-wireless-site-cfg:site-cfg-data/site-tag-configs/site-tag-config"

        data = {'Cisco-IOS-XE-wireless-site-cfg:site-tag-config': [
                {'site-tag-name': ap_tag, 'is-local-site': False}
                ]
        }
        self.__execute_REST(method="PATCH", resource=resource, payload=data)


    def set_ap_tag(self, ap_mac, ap_tag):
        logging.info(f"Changing AP MAC {ap_mac} to have tag {ap_tag}")

        payload = {"ap-tag": 
            {"ap-mac":ap_mac, 
            "site-tag":ap_tag}
        }
        resource = "/Cisco-IOS-XE-wireless-ap-cfg:ap-cfg-data/ap-tags/ap-tag/"
        response = self.__execute_REST(method="PATCH", resource=resource, payload=payload)
        return response

    def get_joined_aps(self):
        resource = "Cisco-IOS-XE-wireless-access-point-oper:access-point-oper-data/capwap-data"
        response = self.__execute_REST(method="GET", resource=resource)

        try:
            json_payload = response.json()
            capwap_data = json_payload['Cisco-IOS-XE-wireless-access-point-oper:capwap-data']
            for entry in capwap_data:
                ethernet_mac = entry["device-detail"]["static-info"]["board-data"]["wtp-enet-mac"]
                serial = entry["device-detail"]["static-info"]["board-data"]["wtp-serial-num"]
                MAC = EUI(ethernet_mac, dialect=mac_unix_expanded)
                self.ap_list[serial] = {
                    "MAC":str(MAC)
                }
        except ValueError as err:
            logging.info(f"No data was returned")
        except AttributeError as err:
            logging.info(f"No data was returned")
        except Exception as err:
            logging.exception(f"Other error: {err}")
        else:
            logging.info(f"Success! {len(self.ap_list)} APs joined")

        return self.ap_list


