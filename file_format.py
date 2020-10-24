import struct
import collections

# SCHEMA rows are either:
# (name, format string)
# (name, format string, raw => nicer value)

class Conv(object):
  def from_raw(self, raw):
    pass

  def to_raw(self, parsed):
    pass

class ListConv(Conv):
  def __init__(self, d):
    self.d = d

  def from_raw(self, raw):
    return self.d[raw]

  def to_raw(self, parsed):
    return self.index(parsed)

class DictConv(Conv):
  def __init__(self, d):
    self.d = d
    self.d_inv = {v: k for k, v in d.iteritems()}

  def from_raw(self, raw):
    return self.d[raw]

  def to_raw(self, parsed):
    return self.d_inv[parsed]

class AddConv(Conv):
  def __init__(self, amount):
    self.amount = amount

  def from_raw(self, raw):
    return raw + self.amount

  def to_raw(self, parsed):
    return parsed - self.amount

class MulConv(Conv):
  def __init__(self, amount):
    self.amount = amount

  def from_raw(self, raw):
    return raw * self.amount

  def to_raw(self, parsed):
    return parsed / self.amount

class BoolConv(Conv):
  def from_raw(self, raw):
    return bool(raw)

  def to_raw(self, parsed):
    return int(parsed)

class BitFlags(Conv):

  def from_raw(self, raw):
    # to binary string, then reverse
    bits = ("{:016b}".format(raw))[::-1]
    return [bool(int(x)) for x in bits]

  def to_raw(self, parsed):
    # bool to bit to string, reversed again
    bits = [str(int(x)) for x in parsed][::-1]
    bits_str = ''.join(bits)
    return int(bits_str, 2) # parse binary string

MOTION_PARAMETERS = DictConv({0 : 'none', 15 : 'portamento', 16 : 'voice_mode_depth', 17 : 'voice_mode_type', 18 : 'vco_1_wave', 19 : 'vco_1_octave', 20 : 'vco_1_pitch', 21 : 'vco_1_shape', 22 : 'vco_2_wave', 23 : 'vco_2_octave', 24 : 'vco_2_pitch', 25 : 'vco_2_shape', 26 : 'sync', 27 : 'ring', 28 : 'cross_mod_depth', 29 : 'multi_engine_type', 30 : 'multi_engine_noise_type', 31 : 'multi_engine_vpm_type', 33 : 'multi_shape_noise', 34 : 'multi_shape_vpm', 35 : 'multi_shape_user', 36 : 'multi_shift_shape_noise', 37 : 'multi_shift_shape_vpm', 38 : 'multi_shift_shape_user', 39 : 'vco_1_level', 40 : 'vco_2_level', 41 : 'multi_engine_level', 42 : 'cutoff', 43 : 'resonance', 45 : 'keytrack', 46 : 'amp_eg_attack', 47 : 'amp_eg_decay', 48 : 'amp_eg_sustain', 49 : 'amp_eg_release', 50 : 'eg_attack', 51 : 'eg_decay', 52 : 'eg_int', 53 : 'eg_target', 54 : 'lfo_wave', 55 : 'lfo_mode', 56 : 'lfo_rate', 57 : 'lfo_int', 58 : 'lfo_target', 59 : 'mod_fx_on_off', 66 : 'mod_fx_time', 67 : 'mod_fx_depth', 68 : 'delay_on_off', 70 : 'delay_time', 71 : 'delay_depth', 72 : 'reverb_on_off', 74 : 'reverb_time', 75 : 'reverb_depth', 126 : 'pitch_bend', 129 : 'gate_time'})

class MotionParameter(Conv):

  def from_raw(self, raw):
    param = MOTION_PARAMETERS.from_raw(raw >> 8)
    motion_on = bool(raw & 1)
    smooth_on = bool((raw & 2) >> 1)
    return collections.OrderedDict([('parameter', param), ('motion_on', motion_on), ('smooth_on', smooth_on)])

  def to_raw(self, parsed):
    param = MOTION_PARAMETERS.ro_raw(parsed['parameter'])
    motion_on = int(parsed['motion_on'])
    smooth_on = int(parsed['smooth_on'])
    raw = param << 8
    raw = raw | motion_on
    raw = raw | (smooth_on << 1)

    return raw

HEADER_SCHEMA = ('magic','<4s')

VOICE_MODES = ListConv(['none', 'arp', 'chord', 'unison','poly'])
VCO_WAVES = ListConv(['sqr', 'tri', 'saw'])
OCTAVE_FEET = ListConv([16, 8, 4, 2])
MULTI_TYPES = ListConv(['noise','vpm','user'])
NOISE_TYPES = ListConv(['high','low','peak','decim'])
VPM_WAVES = ListConv(['sin1','sin2','sin3','sin4','saw1','saw2','squ1','squ2','fat1','fat2','air1','air2','decay1','decay2','creep','throat'])
DRIVE = ListConv([0, 50, 100])
TRACK = ListConv([0, 50, 100])
EG_TARGETS = ListConv(['cutoff', 'pitch2', 'pitch'])
LFO_MODES = ListConv(['1-shot','normal','bpm'])
LFO_TARGETS = ListConv(['cutoff', 'shape', 'pitch'])
MOD_FX_TYPES = ListConv(['chorus','ensemble','phaser','flanger','user'])
CHORUS_TYPES = ListConv(['stereo','light','deep','triphase','harmonic','mono','feedback','vibrato'])
ENSEMBLE_TYPES = ListConv(['stereo','light','mono'])
PHASER_TYPES = ListConv(['stereo','fast','orange','small','small reso','black','formant','twinkle'])
FLANGER_TYPES = ListConv(['stereo','light','mono','high sweep','mid sweep','pan sweep','mono sweep','triphase'])
DELAY_TYPES = ListConv(['stereo','mono','ping pong','hipass','tape','one tap','stereo bpm','mono bpm','ping bpm','hipass bpm','tape bpm','doubling','user1','user2','user3','user4','user5','user6','user7','user8'])
REVERB_TYPES = ListConv(['hall','smooth','arena','plate','room','early ref','space','riser','submarine','horror','user1','user2','user3','user4','user5','user6','user7','user8'])
CV_IN_MODES = ListConv(['modulation','cv_gate_+','cv_gate_-'])
ASSIGN_PARAMETERS = ListConv(['gate_time','portamento','v_m_depth','vco_1_pitch','vco_1_shape','vco_2_pitch','vco_2_shape','cross_mod','multi_shape','vco_1_level','vco_2_level','multi_level','cutoff','resonance','a_eg_attack','a_eg_decay','a_eg_sustain','a_eg_release','eg_attack','eg_decay','eg_int','lfo_rate','lfo_int','mod_fx_speed','mod_fx_depth','reverb_time','reverb_depth','delay_time','delay_depth'])
MICRO_TUNING = DictConv({0 : 'equal_temp', 1 : 'pure_major', 2 : 'pure_minor', 3 : 'pythagorean', 4 : 'werckmeister', 5 : 'kirnburger', 6 : 'slendro', 7 : 'pelog', 8 : 'ionian', 9 : 'dorian', 10 : 'aeolian', 11 : 'major_penta', 12 : 'minor_penta', 13 : 'reverse', 14 : 'afx001', 15 : 'afx002', 16 : 'afx003', 17 : 'afx004', 18 : 'afx005', 19 : 'afx006', 128 : 'user_scale_1', 129 : 'user_scale_2', 130 : 'user_scale_3', 131 : 'user_scale_4', 132 : 'user_scale_5', 133 : 'user_scale_6', 134 : 'user_octave_1', 135 : 'user_octave_2', 136 : 'user_octave_3', 137 : 'user_octave_4', 138 : 'user_octave_5', 139 : 'user_octave_6'})
LFO_TARGET_OSC = ListConv(['all','vco1+vco2','vco2','multi'])
MULTI_ROUTING = ListConv(['pre_vcf', 'post_vcf'])
PORTAMENTO_MODE = ListConv(["auto","on"])
STEP_RESOLUTIONS = ListConv(["1/16","1/8","1/4","1/2","1/1"])


FILE_SCHEMA = [
  HEADER_SCHEMA,
  ('program_name','12s'),
  ('octave','B', AddConv(2)),
  ('portamento','B'),
  ('key_trig','B', BoolConv()),
  ('voice_mode_depth','H'),
  ('voice_mode_type','B', VOICE_MODES),
  ('vco_1_wave','B', VCO_WAVES),
  ('vco_1_octave_feet','B', OCTAVE_FEET),
  ('vco_1_pitch','H'),
  ('vco_1_shape','H'),
  ('vco_2_wave','B', VCO_WAVES),
  ('vco_2_octave_feet','B', OCTAVE_FEET),
  ('vco_2_pitch','H'),
  ('vco_2_shape','H'),
  ('sync','B', BoolConv()),
  ('ring','B', BoolConv()),
  ('cross_mod_depth','H'),
  ('multi_type','B', MULTI_TYPES),
  ('multi_noise_type','B', NOISE_TYPES),
  ('multi_vpm_wave','B', VPM_WAVES),
  ('multi_user_osc','B', AddConv(1)),
  ('multi_shape_noise','H'),
  ('multi_shape_vpm','H'),
  ('multi_shape_user','H'),
  ('multi_shift_shape_noise','H'),
  ('multi_shift_shape_vpm','H'),
  ('multi_shift_shape_user_osc','H'),
  ('vco_1_level','H'),
  ('vco_2_level','H'),
  ('multi_level','H'),
  ('cutoff','H'),
  ('resonance','H'),
  ('drive','B', DRIVE),
  ('keyboard_track','B', TRACK),
  ('amp_eg_attack','H'),
  ('amp_eg_decay','H'),
  ('amp_eg_sustain','H'),
  ('amp_eg_release','H'),
  ('eg_attack','H'),
  ('eg_decay','H'),
  ('eg_int','H'),
  ('eg_target','B', EG_TARGETS),
  ('lfo_wave','B', VCO_WAVES),
  ('lfo_mode','B', LFO_MODES),
  ('lfo_rate','H'),
  ('lfo_int','H'),
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
  ('x+_bend_range','B'),
  ('x-_bend_range','B', MulConv(-1)),
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
  ('scale_key','B'),
  ('program_tuning','B'),
  ('lfo_key_sync','B', BoolConv()),
  ('lfo_voice_sync','B', BoolConv()),
  ('lfo_target_osc','B', LFO_TARGET_OSC),
  ('cutoff_velocity','B'),
  ('amp_velocity','B'),
  ('multi_octave','B', OCTAVE_FEET),
  ('multi_routing','B', MULTI_ROUTING),
  ('eg_legato_on','B', BoolConv()),
  ('portamento_mode','B', PORTAMENTO_MODE),
  ('portamento_bpm_sync_on','B', BoolConv()),
  ('program_level','B'),
  ('vpm_param1','B', AddConv(-100)),
  ('vpm_param2','B', AddConv(-100)),
  ('vpm_param3','B', AddConv(-100)),
  ('vpm_param4','B', AddConv(-100)),
  ('vpm_param5','B', AddConv(-100)),
  ('vpm_param6','B', AddConv(-100)),
  ('user_param1','B'),
  ('user_param2','B'),
  ('user_param3','B'),
  ('user_param4','B'),
  ('user_param5','B'),
  ('user_param6','B'),
  ('user_param_type','H'),
  ('program_transpose','B', AddConv(-13)),
  ('delay_dry_wet','H'),
  ('reverb_dry_wet','H'),
  ('midi_after_touch_assign','B', ASSIGN_PARAMETERS),
  ('pred','4s'),
  ('sq','2s'),
  ('seq_active_steps','H', BitFlags()),
  ('bpm','H'),
  ('seq_step_length','B'),
  ('seq_step_resolution','B', STEP_RESOLUTIONS),
  ('swing','B', AddConv(-75)),
  ('default_gate_time','B'),
  ('seq_steps_on','H', BitFlags()),
  ('seq_steps_motion_on','H', BitFlags()),
  ('seq_motion_1_param','H', MotionParameter()),
  ('seq_motion_2_param','H', MotionParameter()),
  ('seq_motion_3_param','H', MotionParameter()),
  ('seq_motion_4_param','H', MotionParameter()),
  ('seq_steps_motion_1_on','H', BitFlags()),
  ('seq_steps_motion_2_on','H', BitFlags()),
  ('seq_steps_motion_3_on','H', BitFlags()),
  ('seq_steps_motion_4_on','H', BitFlags()),
  ('step_1_event_data','52s'),
  ('step_2_event_data','52s'),
  ('step_3_event_data','52s'),
  ('step_4_event_data','52s'),
  ('step_5_event_data','52s'),
  ('step_6_event_data','52s'),
  ('step_7_event_data','52s'),
  ('step_8_event_data','52s'),
  ('step_9_event_data','52s'),
  ('step_10_event_data','52s'),
  ('step_11_event_data','52s'),
  ('step_12_event_data','52s'),
  ('step_13_event_data','52s'),
  ('step_14_event_data','52s'),
  ('step_15_event_data','52s'),
  ('step_16_event_data','52s'),
  ('arp_gate_time','B'),
  ('arp_rate','B')
]

STEP_EVENT_SCHEMA = [
  ('note_1', '<b'),
  ('note_2', 'b'),
  ('note_3', 'b'),
  ('note_4', 'b'),
  ('note_5', 'b'),
  ('note_6', 'b'),
  ('note_7', 'b'),
  ('note_8', 'b'),
  ('velocity_1', 'b'),
  ('velocity_2', 'b'),
  ('velocity_3', 'b'),
  ('velocity_4', 'b'),
  ('velocity_5', 'b'),
  ('velocity_6', 'b'),
  ('velocity_7', 'b'),
  ('velocity_8', 'b'),
  ('gate_time_1', 'b'),
  ('gate_time_2', 'b'),
  ('gate_time_3', 'b'),
  ('gate_time_4', 'b'),
  ('gate_time_5', 'b'),
  ('gate_time_6', 'b'),
  ('gate_time_7', 'b'),
  ('gate_time_8', 'b'),
  ('motion_slot_1_data_1', 'b'),
  ('motion_slot_1_data_2','b'),
  ('motion_slot_1_data_3','b'),
  ('motion_slot_1_data_4','b'),
  ('motion_slot_1_data_5','b'),
  ('motion_slot_1_data_6','b'),
  ('motion_slot_1_data_7','b'),
  ('motion_slot_2_data_1','b'),
  ('motion_slot_2_data_2','b'),
  ('motion_slot_2_data_3','b'),
  ('motion_slot_2_data_4','b'),
  ('motion_slot_2_data_5','b'),
  ('motion_slot_2_data_6','b'),
  ('motion_slot_2_data_7','b'),
  ('motion_slot_3_data_1','b'),
  ('motion_slot_3_data_2','b'),
  ('motion_slot_3_data_3','b'),
  ('motion_slot_3_data_4','b'),
  ('motion_slot_3_data_5','b'),
  ('motion_slot_3_data_6','b'),
  ('motion_slot_3_data_7','b'),
  ('motion_slot_4_data_1','b'),
  ('motion_slot_4_data_2','b'),
  ('motion_slot_4_data_3','b'),
  ('motion_slot_4_data_4','b'),
  ('motion_slot_4_data_5','b'),
  ('motion_slot_4_data_6','b'),
  ('motion_slot_4_data_7','b'),
]

def unpack(binary, structure):
  format_string = ''.join(map(lambda x: x[1], structure))
  unpacked = struct.unpack(format_string, binary)

  if len(unpacked) != len(structure):
    raise ValueError("Expected to get back %d elements from struct.unpack but got %d" % (len(structure), len(unpacked)))

  res = collections.OrderedDict()

  for i,raw in enumerate(unpacked):
    name = structure[i][0]

    val = raw

    if len(structure[i]) == 3:
      # apply conv
      conv = structure[i][2]
      val = conv.from_raw(raw)

    res[name] = val

  return res

