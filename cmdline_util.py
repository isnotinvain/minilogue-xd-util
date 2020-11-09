'''
supports:
single number: 17
range: 1:2
'''
def patch_number_expr(s):
  if ':' in s:
    (start, stop) = (int(x) - 1 for x in s.split(':',1))

    if start < 0:
      raise ValueError('Patch numbers must be >= 1')

    if start >= stop:
      raise ValueError('Patch range can\'t have start >= stop')

    return xrange(start, stop + 1)
  else:
    p = int(s) - 1

    if p < 0:
      raise ValueError('Patch numbers must be >= 1')
    return xrange(p, p + 1)
