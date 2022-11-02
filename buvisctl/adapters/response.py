class AdapterResponse:
  def __init__(self, code, message):
    self.code = code
    self.message = message

  def is_ok(self):
    return self.code == 0
