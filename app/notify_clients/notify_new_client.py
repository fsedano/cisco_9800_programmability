#!/usr/bin/python3

from lxml import etree
import lxml.etree as ET
from ncclient import manager
from ncclient.xml_ import to_ele

from phonecaller import PhoneCaller
import xmlutils

#### Edit the IP and username below to match your controller

controller = {
    "ip":"<your controller private IP address>",
    "user":"<your pod controller username>",
    "password":"Vimlab123@"
}

#### Enter the phone number to be notified - International format
phone_number = "+411122334455"

#### XPATH to monitor for changes
filter = "<enter your XPATH HERE>"

#### The generic NETCONF notification filter
rpc = """
<establish-subscription xmlns="urn:ietf:params:xml:ns:yang:ietf-event-notifications"
    xmlns:yp="urn:ietf:params:xml:ns:yang:ietf-yang-push">
    <stream>yp:yang-push</stream>
    <yp:xpath-filter>%s</yp:xpath-filter>
    <yp:dampening-period>0</yp:dampening-period>
</establish-subscription>
"""

# This will replace the '%s' on the rpc with the 'filter' variable
rpc = rpc % (filter)

# Initialize an empty set (similar to an array) to hold
# the list of clients currently connected to our controller
currentclients = set()

# Create our PhoneCaller object, and pass the phone number to it
phone = PhoneCaller(phone_number)


with manager.connect(host=controller['ip'],
                        port=830,
                        username=controller['user'],
                        password=controller['password'],
                        hostkey_verify=False) as m:

    ### Subscribe to the NETCONF notification
    print(f"Sending subscription: {rpc}")
    response = m.dispatch(to_ele(rpc))

    while True:
        #  This will block until the controller notifies us
        print("*************************")
        print("Waiting for notifications")
        print("*************************")
        n = m.take_notification()
        print(f"Received notification!\n")

        # Convert the notification into an XML object so we can parse it
        root = ET.fromstring(n.notification_xml.encode("utf-8"))
        print(f"XML is {ET.tostring(root, pretty_print=True).decode()}")

        # Go thru the list of returned client IP addresses and for each client IP...
        for client_ip in root.iter('{http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-client-oper}ip-addr'):
            if xmlutils.is_delete(root):
                # If the operation was a deletion, remove the client IP from the list
                currentclients.discard(client_ip.text)
            else:
                # Else, add the client IP to the list
                currentclients.add(client_ip.text)

        # Now our list is updated. We send it to our phone notifier object and wait again
        # to be called from the controller on next change
        print(f"Current client list is {list(currentclients)}")

        ## Add here a call to notify_changes method of phone object



