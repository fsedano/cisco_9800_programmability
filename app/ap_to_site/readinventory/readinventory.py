import csv

class Inventory:
    def __init__(self, filename):
        self.filename = filename
        self.inventory_data = {}
    def read(self):
        with open("AP_Inventory.csv", encoding='utf-8') as f:
            data = csv.reader(f, delimiter=',')
            next(data, None)
            for row in data:
                if len(row) > 0:
                    serial = row[0]
                    tag = row[1]
                    self.inventory_data[serial] = {
                        "tag":tag
                    }
            return self.inventory_data

