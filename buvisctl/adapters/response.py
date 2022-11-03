class AdapterResponse:

    def __init__(self, code=0, message=""):
        self.code = code
        self.message = message

    def is_ok(self):
        return self.code == 0

    def is_nok(self):
        return self.code != 0
