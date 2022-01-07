import logging
from readinventory import Inventory
from c9800 import C9800
import argparse

## Set logging level and format
logging.basicConfig(level=logging.INFO, format="%(asctime)-15s (%(levelname)s) %(message)s")

## Parse command line arguments.
parser = argparse.ArgumentParser(description="Utility to update AP tag based on serial number")
parser.add_argument('-user', help='c9800 username', required=True)
parser.add_argument('-password', help='c9800 password', required=True)
parser.add_argument('-wlc_ip', help='c9800 IP address', required=True)
args=parser.parse_args()

# Create an object of type C9800 and store it in the wlc variable
wlc = C9800(args.wlc_ip, args.user, args.password)

# Call our wlc object and ask for the list of joined APs
aps = wlc.get_joined_aps()

# Create an Inventory object, read the file content and store it in the inventory variable
inventory = Inventory('AP_Inventory.csv').read()

# We have now the list of joined AP serial numbers (in aps) and the list of APs in inventory (inventory)

# Traverse the joined AP list. It has the following format:
"""
 {
    'FGL2102AACG': {'MAC': 'cc:16:7e:dc:27:d8'},
    'FGL2102AACX': {'MAC': 'cc:16:7e:dc:27:d9'}
}
 """

for ap_serial in aps:
    # We have the serial number now in the ap_serial variable. Check if this serial number
    # is in the inventory
    if ap_serial in inventory:
        # If it is in the inventory, update the tag
        ap_inventory = inventory[ap_serial]
        ap_joined_info = aps[ap_serial]
        ap_joined_mac = ap_joined_info['MAC']
        ap_tag = ap_inventory['tag']

        # Create the tag on the 9800
        wlc.create_site_tag(ap_tag)

        # Assign the AP to this tag
        wlc.set_ap_tag(ap_joined_mac, ap_tag)
