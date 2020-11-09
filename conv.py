'''
Conv converts a value from it's on-file represnetion to a more
programmer / python friendly value. This transform should be loss-less,
so it's not intended for pretty printing (which can be lossy).

General strategy I've taken here is to convert numeric types to
their actual numeric value (applying any shifts needed)
but only if that can be done losslessly, and
enum-like types to strings. Bitsets are converted to lists of true/false.
'''

import parser

'''
Conv() on its own is a no-op
'''
class Conv(object):
  def from_file_repr(self, file_repr):
    return file_repr

  def to_file_repr(self, idiomatic):
    return idiomatic

'''
Treats the file representation as the index into a list.
Used for all the enum-like fields, more convenient than DictConv for
contiguous values.
'''
class ListConv(Conv):
  def __init__(self, items):
    self.items = items

  def from_file_repr(self, file_repr):
    if file_repr >= len(self.items):
      raise ValueError('index {} out of range for {}'.format(file_repr, self.items))
    return self.items[file_repr]

  def to_file_repr(self, idiomatic):
    return self.items.index(idiomatic)

'''
Treats the file representation as the key in a dictionary.
Used for all the enum-like fields that aren't contiguous.
'''
class DictConv(Conv):
  def __init__(self, d):
    self.d = d
    self.d_inv = {v: k for k, v in d.iteritems()}

  def from_file_repr(self, file_repr):
    return self.d[file_repr]

  def to_file_repr(self, idiomatic):
    return self.d_inv[idiomatic]

'''
Adds `amount` to the file representation.
For numeric types that need to be offset by a certain amount.
A lot of file representations are 0 indexed in the file but 1 indexed in the minilogue xd LED display.
Also some of the file representations are unsigned, offset by 100 or similar to support negative values.
'''
class AddConv(Conv):
  def __init__(self, amount):
    self.amount = amount

  def from_file_repr(self, file_repr):
    return file_repr + self.amount

  def to_file_repr(self, idiomatic):
    return idiomatic - self.amount

'''
Same as AddConv but multiplies by an amount instead of adds.
In order to be lossless should only use integers.
'''
class MulConv(Conv):
  def __init__(self, amount):
    self.amount = amount

  def from_file_repr(self, file_repr):
    return file_repr * self.amount

  def to_file_repr(self, idiomatic):
    return idiomatic / self.amount

'''
0 means False
1 means True
'''
class BoolConv(Conv):
  def from_file_repr(self, file_repr):
    return bool(file_repr)

  def to_file_repr(self, idiomatic):
    return int(idiomatic)

'''
For when the file representation is a bitset / bitflag which is annoying to work
with in python. Converts the int bitset to a list of True/False.

TODO: Not sure if this gets the order backwards or not yet.
'''
class BitFlags(Conv):

  def from_file_repr(self, file_repr):
    # to binary string, then reverse
    # TODO: this needs confirming
    bits = ("{:016b}".format(file_repr))[::-1]
    return [bool(int(x)) for x in bits]

  def to_file_repr(self, idiomatic):
    # bool to bit to string, reversed again
    bits = [str(int(x)) for x in idiomatic][::-1]
    bits_str = ''.join(bits)
    return int(bits_str, 2) # parse binary string

'''
For the parts of the file that are nested / have sub-structures.
Given a schema, will parse the field's bytes using parser.parse
'''
class NestedConv(Conv):
  def __init__(self, schema):
    self.schema = schema

  def from_file_repr(self, file_repr):
    return parser.parse(file_repr, self.schema)

  def to_file_repr(self, parsed):
    return parsed.serialize()
