# TODO: Rewor
class Variables:
    def __init__(self, data):
        self.data = data

    @property
    def vars(self):
        return self.data["variables"]

    def set(self, key, value):
        for item in self.vars:
            if item["name"] == key:
                item["value"] = value
                break
        else:
            self.set_first_free(key, value)

    def get(self, key):
        for item in self.vars:
            if item["name"] == key:
                return item

    def is_free(self, item):
        return item["name"].strip() == "" and item["value"].strip() == ""

    def set_first_free(self, key, value):
        for item in self.vars:
            if self.is_free(item):
                item["name"] = key
                item["value"] = value
                break