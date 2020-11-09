'''
Serializes and deserializes the binary contents of a minilogue xd prog_bin file
Much of this file is taken and modified from https://gist.github.com/gekart/b187d3c16e6160571ccfcf6c597fea3f
Thank you @gekart!
'''

import collections, struct, traceback, inspect
from conv import *
import json

# 124 is an unknown value used in a factory preset
MOTION_PARAMETERS = DictConv({0 : 'NONE', 15 : 'PORTAMENTO', 16 : 'VOICE MODE: DEPTH', 17 : 'VOICE MODE: TYPE', 18 : 'VCO1: WAVE', 19 : 'VCO1: OCTAVE', 20 : 'VCO1: PITCH', 21 : 'VCO1: SHAPE', 22 : 'VCO2: WAVE', 23 : 'VCO2: OCTAVE', 24 : 'VCO2: PITCH', 25 : 'VCO2: SHAPE', 26 : 'SYNC', 27 : 'RING', 28 : 'CROSS MOD DEPTH', 29 : 'MULTI ENGINE: TYPE', 30 : 'MULTI ENGINE: NOISE TYPE', 31 : 'MULTI ENGINE: VPM TYPE', 33 : 'MULTI SHAPE: NOISE', 34 : 'MULTI SHAPE: VPM', 35 : 'MULTI SHAPE: USER', 36 : 'MULTI SHIFT SHAPE: NOISE', 37 : 'MULTI SHIFT SHAPE: VPM', 38 : 'MULTI SHIFT SHAPE: USER', 39 : 'VCO1: LEVEL', 40 : 'VCO2: LEVEL', 41 : 'MULTI ENGINE: LEVEL', 42 : 'CUTOFF', 43 : 'RESONANCE', 45 : 'KEYTRACK', 46 : 'AMP EG: ATTACK', 47 : 'AMP EG: DECAY', 48 : 'AMP EG: SUSTAIN', 49 : 'AMP EG: RELEASE', 50 : 'EG: ATTACK', 51 : 'EG: DECAY', 52 : 'EG: INT', 53 : 'EG: TARGET', 54 : 'LFO: WAVE', 55 : 'LFO: MODE', 56 : 'LFO: RATE', 57 : 'LFO: INT', 58 : 'LFO: TARGET', 59 : 'MOD FX: ON/OFF', 66 : 'MOD FX: TIME', 67 : 'MOD FX: DEPTH', 68 : 'DELAY: ON/OFF', 70 : 'DELAY: TIME', 71 : 'DELAY: DEPTH', 72 : 'REVERB: ON/OFF', 74 : 'REVERB: TIME', 75 : 'REVERB: DEPTH', 124: '???', 126 : 'PITCH BEND', 129 : 'GATE TIME'})

class MotionParameter(Conv):

  def from_file_repr(self, file_repr):
    param = MOTION_PARAMETERS.from_file_repr(file_repr >> 8)
    motion_on = bool(file_repr & 1)
    smooth_on = bool((file_repr & 2) >> 1)
    return collections.OrderedDict([('parameter', param), ('motion_on', motion_on), ('smooth_on', smooth_on)])

  def to_file_repr(self, parsed):
    param = MOTION_PARAMETERS.to_file_repr(parsed['parameter'])
    motion_on = int(parsed['motion_on'])
    smooth_on = int(parsed['smooth_on'])
    file_repr = param << 8
    file_repr = file_repr | motion_on
    file_repr = file_repr | (smooth_on << 1)

    return file_repr

class NestedConv(Conv):
  def __init__(self, structure):
    self.structure = structure

  def from_file_repr(self, file_repr):
    return unpack(file_repr, self.structure)

  def to_file_repr(self, parsed):
    return pack(parsed, self.structure)

def pitch_cents(value):
  if 0 <= value <= 4:
    cents = -1200
  elif 4 <= value <= 356: #-1200 ~ -256 (Cent)
    cents = (value - 356) * 944 / 352 - 256
  elif 356 <= value <= 476: # -256 ~  -16 (Cent)
    cents = (value - 476) * 2 - 16
  elif 476 <= value <= 492: #  -16 ~   0 (Cent)
    cents = value - 492
  elif 492 <= value <= 532: #    0 (Cent)
    cents = 0
  elif 532 <= value <= 548: #    0 ~   16 (Cent)
    cents = value - 532
  elif 548 <= value <= 668: #   16 ~  256 (Cent)
    cents = (value - 548) * 2 + 16
  elif 668 <= value <= 1020: #  256 ~ 1200 (Cent)
    cents = (value - 668) * 944 / 352 + 256
  elif 1020 <= value <= 1023: # 1200 (Cent)
    cents = 1200
  else:
    raise ValueError('Invalid pitch cents: {}'.format(value))

  return '{} Cent'.format(cents)

def eg_int(val):
  if 0 <= val <= 11:
    return '-100%'
  if 11 <= val <= 492:
    return str(- ((492 - val) * (492 - val) * 4641 * 100) / 0x40000000) + '%'
  if 492 <= val <= 532:
    return '0%'
  if 532 <= val <= 1013:
    return str(((val - 532) * (val - 532) * 4641 * 100) / 0x40000000) + '%'
  if 1013 <= val <= 1023:
    return '100%'

def lfo_rate(data, val):
  if data['lfo_mode'] == 'BPM':
    if 0 <= val <= 63:
      return '4'
    if 64 <= val <= 127:
      return '2'
    if 128 <= val <= 191:
      return '1'
    if 192 <= val <= 255:
      return '3/4'
    if 256 <= val <= 319:
      return '1/2'
    if 320 <= val <= 383:
      return '3/8'
    if 384 <= val <= 447:
      return '1/3'
    if 448 <= val <= 511:
      return '1/4'
    if 512 <= val <= 575:
      return '3/16'
    if 576 <= val <= 639:
      return '1/6'
    if 640 <= val <= 703:
      return '1/8'
    if 704 <= val <= 767:
      return '1/12'
    if 768 <= val <= 831:
      return '1/16'
    if 832 <= val <= 895:
      return '1/24'
    if 896 <= val <= 959:
      return '1/32'
    if 960 <= val <= 1023:
      return '1/36'

  return str(val)

def bit_flag_pp(bits):
  res = ''
  for b in bits:
    if b:
      res += '+'
    else:
      res += '-'
  return res

def json_pp(item):
  return json.dumps(item)

def range_dict(rd, val):
  for upper, res in rd:
    if val <= upper:
      return res

  raise ValueError('Value out of range {}\n{}'.format(val, rd))

ARP_RD = [
  (78,   'MANUAL 1'),
  (156,  'MANUAL 2'),
  (234,  'RISE 1'),
  (312,  'RISE 2'),
  (390,  'FALL 1'),
  (468,  'FALL 2'),
  (546,  'RISE FALL 1'),
  (624,  'RISE FALL 2'),
  (702,  'POLY 1'),
  (780,  'POLY 2'),
  (858,  'RANDOM 1'),
  (936,  'RANDOM 2'),
  (1023, 'RANDOM 3')
]

CHORD_RD = [
  (1,    'MONO'),
  (73,   '5th'),
  (146,  'sus2'),
  (219,  'm'),
  (292,  'Maj'),
  (365,  'sus4'),
  (438,  'm7'),
  (511,  '7'),
  (585,  '7sus4'),
  (658,  'Maj7'),
  (731,  'aug'),
  (804,  'dim'),
  (877,  'm7b5'),
  (950,  'mMaj7'),
  (1023, 'Maj7b5')
]

def voice_mode_depth(data, val):
  if data['voice_mode_type'] == 'ARP':
    return range_dict(ARP_RD, val)

  if data['voice_mode_type'] == 'CHORD':
    return range_dict(CHORD_RD, val)

  if data['voice_mode_type'] == 'UNISON':
    return str(val * 50 / 1023) + ' Cent'

  if data['voice_mode_type'] == 'POLY':
    if val < 256:
      return 'POLY'
    else:
      return 'DUO' + str(val * 50 / 1023) + ' Cent'

  raise ValueError('Unrecognized voice mode state')

def add_sign(val):
  res = ''
  if val >= 0.0:
    res = res + '+'

  return res + str(val)

def program_level(val):
  if val == 102:
    level = 0
  else:
    level = (float(val) - 12) / 5 - 18

  res = ''
  if level >= 0:
    res = res + '+'

  return '{:.1f} dB'.format(level)

def user_param_curry(i):
  def tmp(data, val):
    return user_param(data, val, i)
  return tmp

def user_param(data, val, i):
  if not 1 <= i <= 6:
    raise ValueError("Invalid user param: " + str(i))

  shift_by = (i - 1) * 2
  param_type = (data['user_param_type'] >> shift_by) & 3

  if param_type == 0:
    # normal percent
    return str(val) + '%'

  if param_type == 1:
    # bipolar percent
    return str(val - 100) + '%'

  if param_type == 2:
    # normal, just add 1
    return val + 1

  if param_type == 3:
    # empty / user osc not used
    return 'N/A'

def pct1023(val):
  fraction = float(val) / 1023
  pct = fraction * 100
  return '{:.1f}%'.format(pct)

HEADER_SCHEMA = ('magic','<4s', Conv(), None)

VOICE_MODES = ListConv(['NONE', 'ARP', 'CHORD', 'UNISON','POLY'])
VCO_WAVES = ListConv(['SQR', 'TRI', 'SAW'])
OCTAVE_FEET = ListConv([16, 8, 4, 2])
MULTI_TYPES = ListConv(['NOISE','VPM','USER'])
NOISE_TYPES = ListConv(['HIGH','LOW','PEAK','DECIM'])
VPM_WAVES = ListConv(['SIN1','SIN2','SIN3','SIN4','SAW1','SAW2','SQU1','SQU2','FAT1','FAT2','AIR1','AIR2','DECAY1','DECAY2','CREEP','THROAT'])
DRIVE = ListConv([0, 50, 100])
TRACK = ListConv([0, 50, 100])
EG_TARGETS = ListConv(['CUTOFF', 'PITCH2', 'PITCH'])
LFO_MODES = ListConv(['1-SHOT','NORMAL','BPM'])
LFO_TARGETS = ListConv(['CUTOFF', 'SHAPE', 'PITCH'])
MOD_FX_TYPES = ListConv(['NONE', 'CHORUS','ENSEMBLE','PHASER','FLANGER','USER'])
CHORUS_TYPES = ListConv(['STEREO','LIGHT','DEEP','TRIPHASE','HARMONIC','MONO','FEEDBACK','VIBRATO'])
ENSEMBLE_TYPES = ListConv(['STEREO','LIGHT','MONO'])
PHASER_TYPES = ListConv(['STEREO','FAST','ORANGE','SMALL','SMALL RESO','BLACK','FORMANT','TWINKLE'])
FLANGER_TYPES = ListConv(['STEREO','LIGHT','MONO','HIGH SWEEP','MID SWEEP','PAN SWEEP','MONO SWEEP','TRIPHASE'])
DELAY_TYPES = ListConv(['STEREO','MONO','PING PONG','HIPASS','TAPE','ONE TAP','STEREO BPM','MONO BPM','PING BPM','HIPASS BPM','TAPE BPM','DOUBLING','USER1','USER2','USER3','USER4','USER5','USER6','USER7','USER8'])
REVERB_TYPES = ListConv(['HALL','SMOOTH','ARENA','PLATE','ROOM','EARLY REF','SPACE','RISER','SUBMARINE','HORROR','USER1','USER2','USER3','USER4','USER5','USER6','USER7','USER8'])
CV_IN_MODES = ListConv(['MODULATION','CV GATE +','CV GATE -'])
ASSIGN_PARAMETERS = ListConv(['GATE TIME','PORTAMENTO','VOICE MODE: DEPTH','VCO1: PITCH','VCO1: SHAPE','VCO2: PITCH','VCO2: SHAPE','CROSS MOD','MULTI: SHAPE','VCO1: LEVEL','VCO2: LEVEL','MULTI: LEVEL','CUTOFF','RESONANCE','AMP EG: ATTACK','AMP EG: DECAY','AMP EG: SUSTAIN','AMP EG: RELEASE','EG: ATTACK','EG: DECAY','EG: INT','LFO: RATE','LFO: INT','MOD FX: SPEED','MOD FX: DEPTH','REVERB: TIME','REVERB: DEPTH','DELAY: TIME','DELAY: DEPTH'])
MICRO_TUNING = DictConv({0 : 'EQUAL TEMP', 1 : 'PURE MAJOR', 2 : 'PURE MINOR', 3 : 'PYTHAGOREAN', 4 : 'WERCKMEISTER', 5 : 'KIRNBURGER', 6 : 'SLENDRO', 7 : 'PELOG', 8 : 'IONIAN', 9 : 'DORIAN', 10 : 'AEOLIAN', 11 : 'MAJOR PENTA', 12 : 'MINOR PENTA', 13 : 'REVERSE', 14 : 'AFX001', 15 : 'AFX002', 16 : 'AFX003', 17 : 'AFX004', 18 : 'AFX005', 19 : 'AFX006', 128 : 'USER SCALE 1', 129 : 'USER SCALE 2', 130 : 'USER SCALE 3', 131 : 'USER SCALE 4', 132 : 'USER SCALE 5', 133 : 'USER SCALE 6', 134 : 'USER OCTAVE 1', 135 : 'USER OCTAVE 2', 136 : 'USER OCTAVE 3', 137 : 'USER OCTAVE 4', 138 : 'USER OCTAVE 5', 139 : 'USER OCTAVE 6'})
LFO_TARGET_OSC = ListConv(['ALL','VCO1 + VCO2','VCO2','MULTI'])
MULTI_ROUTING = ListConv(['PRE VCF', 'POST VCF'])
PORTAMENTO_MODE = ListConv(['AUTO', 'ON'])
STEP_RESOLUTIONS = ListConv(['1/16','1/8','1/4','1/2','1/1'])

STEP_EVENT_SCHEMA = [
  ('note_1', '<B'),
  ('note_2', 'B'),
  ('note_3', 'B'),
  ('note_4', 'B'),
  ('note_5', 'B'),
  ('note_6', 'B'),
  ('note_7', 'B'),
  ('note_8', 'B'),
  ('velocity_1', 'B'),
  ('velocity_2', 'B'),
  ('velocity_3', 'B'),
  ('velocity_4', 'B'),
  ('velocity_5', 'B'),
  ('velocity_6', 'B'),
  ('velocity_7', 'B'),
  ('velocity_8', 'B'),
  ('gate_time_1', 'B'),
  ('gate_time_2', 'B'),
  ('gate_time_3', 'B'),
  ('gate_time_4', 'B'),
  ('gate_time_5', 'B'),
  ('gate_time_6', 'B'),
  ('gate_time_7', 'B'),
  ('gate_time_8', 'B'),
  ('motion_slot_1_data_1', 'B'),
  ('motion_slot_1_data_2', 'B'),
  ('motion_slot_1_data_3', 'B'),
  ('motion_slot_1_data_4', 'B'),
  ('motion_slot_1_data_5', 'B'),
  ('motion_slot_1_data_6', 'B'),
  ('motion_slot_1_data_7', 'B'),
  ('motion_slot_2_data_1', 'B'),
  ('motion_slot_2_data_2', 'B'),
  ('motion_slot_2_data_3', 'B'),
  ('motion_slot_2_data_4', 'B'),
  ('motion_slot_2_data_5', 'B'),
  ('motion_slot_2_data_6', 'B'),
  ('motion_slot_2_data_7', 'B'),
  ('motion_slot_3_data_1', 'B'),
  ('motion_slot_3_data_2', 'B'),
  ('motion_slot_3_data_3', 'B'),
  ('motion_slot_3_data_4', 'B'),
  ('motion_slot_3_data_5', 'B'),
  ('motion_slot_3_data_6', 'B'),
  ('motion_slot_3_data_7', 'B'),
  ('motion_slot_4_data_1', 'B'),
  ('motion_slot_4_data_2', 'B'),
  ('motion_slot_4_data_3', 'B'),
  ('motion_slot_4_data_4', 'B'),
  ('motion_slot_4_data_5', 'B'),
  ('motion_slot_4_data_6', 'B'),
  ('motion_slot_4_data_7', 'B'),
]

FILE_SCHEMA = [
  HEADER_SCHEMA,
  ('name','12s'),
  ('octave','B', AddConv(-2)),
  ('portamento','B'),
  ('key_trig','B', BoolConv()),
  ('voice_mode_depth','H', Conv(), voice_mode_depth),
  ('voice_mode_type','B', VOICE_MODES),
  ('vco_1_wave','B', VCO_WAVES),
  ('vco_1_octave_feet','B', OCTAVE_FEET, lambda x : str(x) + "'"),
  ('vco_1_pitch','H',Conv(),pitch_cents),
  ('vco_1_shape','H'),
  ('vco_2_wave','B', VCO_WAVES),
  ('vco_2_octave_feet','B', OCTAVE_FEET, lambda x : str(x) + "'"),
  ('vco_2_pitch','H', Conv(), pitch_cents),
  ('vco_2_shape','H'),
  ('sync','B', BoolConv()),
  ('ring','B', BoolConv()),
  ('cross_mod_depth','H'),
  ('multi_type','B', MULTI_TYPES),
  ('multi_noise_type','B', NOISE_TYPES),
  ('multi_vpm_wave','B', VPM_WAVES),
  ('multi_user_osc','B', AddConv(1), lambda x : 'USER{}'.format(x)),
  ('multi_shape_noise','H', Conv(), pct1023), # actually varies by noise type
  ('multi_shape_vpm','H', Conv(), pct1023), # actually mod depth
  ('multi_shape_user','H', Conv(), pct1023),
  ('multi_shift_shape_noise','H', Conv(), pct1023), # actually varies by noise type
  ('multi_shift_shape_vpm','H', Conv(), pct1023), # actually ratio offset
  ('multi_shift_shape_user_osc','H', Conv(), pct1023),
  ('vco_1_level','H'),
  ('vco_2_level','H'),
  ('multi_level','H'),
  ('cutoff','H'),
  ('resonance','H'),
  ('drive','B', DRIVE, lambda x : '{}%'.format(x)),
  ('keyboard_track','B', TRACK, lambda x : '{}%'.format(x)),
  ('amp_eg_attack','H'),
  ('amp_eg_decay','H'),
  ('amp_eg_sustain','H'),
  ('amp_eg_release','H'),
  ('eg_attack','H'),
  ('eg_decay','H'),
  ('eg_int','H', Conv(), eg_int),
  ('eg_target','B', EG_TARGETS),
  ('lfo_wave','B', VCO_WAVES),
  ('lfo_mode','B', LFO_MODES),
  ('lfo_rate','H', Conv(), lfo_rate),
  ('lfo_int','H', AddConv(-512)),
  ('lfo_target','B', LFO_TARGETS),
  ('mod_fx_on','B', BoolConv()),
  ('mod_fx_type','B', MOD_FX_TYPES),
  ('mod_fx_chorus','B', CHORUS_TYPES),
  ('mod_fx_ensemble','B', ENSEMBLE_TYPES),
  ('mod_fx_phaser','B', PHASER_TYPES),
  ('mod_fx_flanger','B', FLANGER_TYPES),
  ('mod_fx_user','B', AddConv(1)),
  ('mod_fx_time','H', ),
  ('mod_fx_depth','H'),
  ('delay_on','B', BoolConv()),
  ('delay_type','B', DELAY_TYPES),
  ('delay_time','H'),
  ('delay_depth','H'),
  ('reverb_fx_on','B', BoolConv()),
  ('reverb_type','B', REVERB_TYPES),
  ('reverb_time','H'),
  ('reverb_depth','H'),
  ('x+_bend_range','B', Conv(), add_sign),
  ('x-_bend_range','B', MulConv(-1), add_sign),
  ('y+_assign','B', ASSIGN_PARAMETERS),
  ('y+_range','B', AddConv(-100)),
  ('y-_assign','B', ASSIGN_PARAMETERS),
  ('y-_range','B', AddConv(-100)),
  ('cv_in_mode','B', CV_IN_MODES),
  ('cv_in1_assign','B', ASSIGN_PARAMETERS),
  ('cv_in1_range','B', AddConv(-100)),
  ('cv_in2_assign','B', ASSIGN_PARAMETERS),
  ('cv_in2_range','B', AddConv(-100)),
  ('micro_tuning','B', MICRO_TUNING),
  ('scale_key','B', AddConv(-12), lambda x : add_sign(x) + ' Notes'),
  ('program_tuning','B', AddConv(-50), lambda x : add_sign(x) + ' Cents'),
  ('lfo_key_sync','B', BoolConv()),
  ('lfo_voice_sync','B', BoolConv()),
  ('lfo_target_osc','B', LFO_TARGET_OSC),
  ('cutoff_velocity','B'),
  ('amp_velocity','B'),
  ('multi_octave','B', OCTAVE_FEET, lambda x : str(x) + "'"),
  ('multi_routing','B', MULTI_ROUTING),
  ('eg_legato_on','B', BoolConv()),
  ('portamento_mode','B', PORTAMENTO_MODE),
  ('portamento_bpm_sync_on','B', BoolConv()),
  ('program_level','B', Conv(), program_level),
  ('vpm_param1','B', AddConv(-100)),
  ('vpm_param2','B', AddConv(-100)),
  ('vpm_param3','B', AddConv(-100)),
  ('vpm_param4','B', AddConv(-100)),
  ('vpm_param5','B', AddConv(-100)),
  ('vpm_param6','B', AddConv(-100)),
  ('user_param1','B', Conv(), user_param_curry(1)),
  ('user_param2','B', Conv(), user_param_curry(2)),
  ('user_param3','B', Conv(), user_param_curry(3)),
  ('user_param4','B', Conv(), user_param_curry(4)),
  ('user_param5','B', Conv(), user_param_curry(5)),
  ('user_param6','B', Conv(), user_param_curry(6)),
  ('user_param_type','H', Conv(), None),
  ('program_transpose','B', AddConv(-13), lambda x : '{} Notes'.format(add_sign(x))),
  ('delay_dry_wet','H'),
  ('reverb_dry_wet','H'),
  ('midi_after_touch_assign','B', ASSIGN_PARAMETERS),
  ('pred','4s', Conv(), None),
  ('sq','2s', Conv(), None),
  ('seq_active_steps','H', BitFlags(), bit_flag_pp),
  ('bpm','H', Conv(), lambda x : '{:.1f}'.format(float(x) / 10)),
  ('seq_step_length','B'),
  ('seq_step_resolution','B', STEP_RESOLUTIONS),
  ('swing','B', AddConv(-75)),
  ('default_gate_time','B', Conv(), lambda x: str((x * 100) / 72) + '%'),
  ('seq_steps_on','H', BitFlags(), bit_flag_pp),
  ('seq_steps_motion_on','H', BitFlags(), bit_flag_pp),
  ('seq_motion_1_param','H', MotionParameter(), json_pp),
  ('seq_motion_2_param','H', MotionParameter(), json_pp),
  ('seq_motion_3_param','H', MotionParameter(), json_pp),
  ('seq_motion_4_param','H', MotionParameter(), json_pp),
  ('seq_steps_motion_1_on','H', BitFlags(), bit_flag_pp),
  ('seq_steps_motion_2_on','H', BitFlags(), bit_flag_pp),
  ('seq_steps_motion_3_on','H', BitFlags(), bit_flag_pp),
  ('seq_steps_motion_4_on','H', BitFlags(), bit_flag_pp),
  ('step_1_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_2_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_3_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_4_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_5_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_6_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_7_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_8_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_9_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_10_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_11_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_12_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_13_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_14_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_15_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('step_16_event_data','52s', NestedConv(STEP_EVENT_SCHEMA), None),
  ('arp_gate_time','B', Conv(), lambda x: str((x * 100) / 72) + '%'),
  ('arp_rate','B')
]

class Parsed(object):
  def __init__(self, schema, data):
    self.schema = schema
    self.data = data

  def __getitem__(self, key):
    return self.data[key]

  def __setitem__(self, key, value):
    self.data[key] = value

  def serialize(self):
    return pack(self.data, self.schema)

  def nice_string(self):
    printers = dict((x[0], x[3]) for x in self.schema if len(x) >= 4)

    lines = []
    for k,v in self.data.iteritems():
      pp = printers.get(k, lambda x : str(x))

      if pp:
        if len(inspect.getargspec(pp).args) == 1:
          ppv = pp(v)
        else:
          ppv = pp(self.data, v)

        lines.append('{} => {}'.format(k, ppv))

    return '\n'.join(lines)

def unpack(binary, structure):
  format_string = ''.join(map(lambda x: x[1], structure))
  unpacked = struct.unpack(format_string, binary)

  if len(unpacked) != len(structure):
    raise ValueError('Expected to get back %d elements from struct.unpack but got %d' % (len(structure), len(unpacked)))

  res = collections.OrderedDict()

  for i,file_repr in enumerate(unpacked):
    name = structure[i][0]

    val = file_repr

    if len(structure[i]) >= 3:
      # apply conv
      conv = structure[i][2]
      val = conv.from_file_repr(file_repr)

    res[name] = val

  return res

def pack(data, structure):
  format_string = ''.join(map(lambda x: x[1], structure))

  file_repr_values = []

  for field in structure:
    name = field[0]
    p = data[name]

    if len(field) >= 3:
      # invert conv
      conv = field[2]
      p = conv.to_file_repr(p)

    file_repr_values.append(p)

  return struct.pack(format_string, *file_repr_values)

def assert_header(file_content):
  try:
    magic = unpack(file_content[:4], [HEADER_SCHEMA])
  except:
    traceback.print_exc()
    raise ValueError('Could not unpack magic hader from file, is this in invalid file?')

  if magic['magic'] != 'PROG':
    raise ValueError('File does not begin with magic header PROG')

def deserialize(file_content):

  # first look for magic header as sanity check
  assert_header(file_content)

  unpacked = unpack(file_content, FILE_SCHEMA)

  # seems unlikely but check the magic field again anyway
  if (unpacked['magic'] != 'PROG'):
    raise ValueError('This doesn\'t look like a valid file, magic PROG header incorrect')

  return Parsed(FILE_SCHEMA, unpacked)
