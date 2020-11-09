'''
Conv converts a value from it's on-file represnetion to a more
programmer / python friendly value. This transform should be loss-less,
so it's not intended for pretty printing (which can be lossy).

General strategy I've taken here is to convert numeric types to
their actual numeric value (applying any shifts needed)
but only if that can be done losslessly, and
enum-like types to strings. Bitsets are converted to lists of true/false.
'''
class Conv(object):
  def from_file_repr(self, file_repr):
    return file_repr

  def to_file_repr(self, deserialized):
    return deserialized

class ListConv(Conv):
  def __init__(self, items):
    self.items = items

  def from_file_repr(self, file_repr):
    if file_repr >= len(self.items):
      raise ValueError('index {} out of range for {}'.format(file_repr, self.items))
    return self.items[file_repr]

  def to_file_repr(self, deserialized):
    return self.items.index(deserialized)

class DictConv(Conv):
  def __init__(self, d):
    self.d = d
    self.d_inv = {v: k for k, v in d.iteritems()}

  def from_file_repr(self, file_repr):
    return self.d[file_repr]

  def to_file_repr(self, deserialized):
    return self.d_inv[deserialized]

class AddConv(Conv):
  def __init__(self, amount):
    self.amount = amount

  def from_file_repr(self, file_repr):
    return file_repr + self.amount

  def to_file_repr(self, deserialized):
    return deserialized - self.amount

class MulConv(Conv):
  def __init__(self, amount):
    self.amount = amount

  def from_file_repr(self, file_repr):
    return file_repr * self.amount

  def to_file_repr(self, deserialized):
    return deserialized / self.amount

class BoolConv(Conv):
  def from_file_repr(self, file_repr):
    return bool(file_repr)

  def to_file_repr(self, deserialized):
    return int(deserialized)

class BitFlags(Conv):

  def from_file_repr(self, file_repr):
    # to binary string, then reverse
    bits = ("{:016b}".format(file_repr))[::-1]
    return [bool(int(x)) for x in bits]

  def to_file_repr(self, deserialized):
    # bool to bit to string, reversed again
    bits = [str(int(x)) for x in deserialized][::-1]
    bits_str = ''.join(bits)
    return int(bits_str, 2) # parse binary string
