#!/usr/bin/python3
"""
Code to provision AP tags based on spreadsheet data
"""

import logging
from readinventory import Inventory
from wirelesscontroller import C9800

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s (%(levelname)s) %(message)s")

### Replace IP with the one for your controller
controller = {
    "ip":"10.51.65.200",
    "user":"lab",
    "password":"lab"
}

wlc = C9800(controller["ip"],
    controller["user"],
    controller["password"])

aps = wlc.get_joined_aps()
inventory = Inventory('AP_Inventory.csv').read()

for ap_serial in aps:
    if ap_serial in inventory:
        ap_inventory = inventory[ap_serial]
        ap_joined_info = aps[ap_serial]
        ap_joined_mac = ap_joined_info['MAC']
        ap_tag = ap_inventory['tag']

        wlc.set_site_tag(ap_tag)
        wlc.set_ap_tag(ap_joined_mac, ap_tag)


