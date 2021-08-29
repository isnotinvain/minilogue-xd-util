'''
Parses binary files based on a provided schema, and applies conversions to more idiomatic python values.
Conversions are specified in the given schema via Conv instances.
'''

import collections
import inspect
import struct

'''
A Parsed is dict-like but also carries its schema, and can be serialized back to its binary format.
It can also be pretty printed.

Schema should be a list of tuples, each of which in one of the following forms:
  (name,binary_format) # implies no-op conv + no-op pretty printer
  (name,binary_format, conv) # implies no-op pretty printer
  (name,binary_format, conv, pretty_printer)

binary_format is a string understood by the struct library

conv is an instance of Conv that can handle the value that the struct library
produces based on the given binary_format

pretty_printer is a fucntion or None
  if the function has arity of 1, it should be a function from value => pretty string
  if the function has arity of 2, it should be a function from (parsed, value) => pretty string
    where parsed is the Parsed instance being printed
  if None the field won't be printed at all

if pretty_printer is omitted str(value) will be used
'''
class Parsed(object):
  def __init__(self, schema, data):
    self.schema = schema
    self.data = data

  def __getitem__(self, key):
    return self.data[key]

  def __setitem__(self, key, value):
    self.data[key] = value

  def serialize(self):
    format_string = ''.join(map(lambda x: x[1], self.schema))

    file_repr_values = []

    for field in self.schema:
      name = field[0]
      p = self.data[name]

      if len(field) >= 3:
        # invert conv
        conv = field[2]
        p = conv.to_file_repr(p)

      file_repr_values.append(p)

    return struct.pack(format_string, *file_repr_values)

  def pretty_print(self):
    printers = dict((x[0], x[3]) for x in self.schema if len(x) >= 4)

    lines = []
    for k,v in self.data.items():
      pp = printers.get(k, lambda x : str(x))

      if pp: # if pp is None we don't print anything
        if len(inspect.getargspec(pp).args) == 1:
          ppv = pp(v)
        else:
          ppv = pp(self.data, v)

        lines.append('{} => {}'.format(k, ppv))

    return '\n'.join(lines)

def parse(binary, schema):
  format_string = ''.join(map(lambda x: x[1], schema))
  unpacked = struct.unpack(format_string, binary)

  if len(unpacked) != len(schema):
    raise ValueError('Expected to get back %d elements from struct.unpack but got %d' % (len(schema), len(unpacked)))

  res = collections.OrderedDict()

  for i,file_repr in enumerate(unpacked):
    name = schema[i][0]

    val = file_repr

    if len(schema[i]) >= 3:
      # apply conv
      conv = schema[i][2]
      val = conv.from_file_repr(file_repr)

    res[name] = val

  return Parsed(schema, res)
