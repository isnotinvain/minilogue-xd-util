
class Conv(object):
  def from_raw(self, raw):
    return raw

  def to_raw(self, deserialized):
    return deserialized

class ListConv(Conv):
  def __init__(self, items):
    self.items = items

  def from_raw(self, raw):
    return self.items[raw]

  def to_raw(self, deserialized):
    return self.items.index(deserialized)

class DictConv(Conv):
  def __init__(self, d):
    self.d = d
    self.d_inv = {v: k for k, v in d.iteritems()}

  def from_raw(self, raw):
    return self.d[raw]

  def to_raw(self, deserialized):
    return self.d_inv[deserialized]

class AddConv(Conv):
  def __init__(self, amount):
    self.amount = amount

  def from_raw(self, raw):
    return raw + self.amount

  def to_raw(self, deserialized):
    return deserialized - self.amount

class MulConv(Conv):
  def __init__(self, amount):
    self.amount = amount

  def from_raw(self, raw):
    return raw * self.amount

  def to_raw(self, deserialized):
    return deserialized / self.amount

class BoolConv(Conv):
  def from_raw(self, raw):
    return bool(raw)

  def to_raw(self, deserialized):
    return int(deserialized)

class BitFlags(Conv):

  def from_raw(self, raw):
    # to binary string, then reverse
    bits = ("{:016b}".format(raw))[::-1]
    return [bool(int(x)) for x in bits]

  def to_raw(self, deserialized):
    # bool to bit to string, reversed again
    bits = [str(int(x)) for x in deserialized][::-1]
    bits_str = ''.join(bits)
    return int(bits_str, 2) # parse binary string
