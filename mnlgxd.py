# This file is from https://gist.github.com/gekart/b187d3c16e6160571ccfcf6c597fea3f
# Which has no license
# I plan to fork this file for my own use and will need to reach out to gekart about attribution
###############################

# Use this file to parse the structure of your minilogue programs and libraries (sound banks)
# this makes it easy to understand and document a finished sound
# run "python mnlgxd.py test.mnlgxdprog" to print the sound in a program name test.mnlgxdprog
# or "python mnlgxd.py test.mnlgxdlib 1" to print the second sound in the bank named test.mnlgxdlib

import struct, sys, zipfile

fileStructure = [
  ("MAGIC", "<4s"),
  ("PROGRAM NAME", "12s"),
  ("OCTAVE", "B", "val - 2"),
  ("PORTAMENTO", "B"),
  ("KEY TRIG", "B", "['Off','On'][val]"),
  ("VOICE MODE DEPTH", "H", "voice_mode_depth(val)"),
  ("VOICE MODE TYPE", "B", "['None', 'ARP', 'CHORD', 'UNISON','POLY'][val]"),
  ("VCO 1 WAVE", "B", '["SQR","TRI","SAW"][val]'),
  ("VCO 1 OCTAVE", "B", '["16\'","8\'","4\'","2\'"][val]'),
  ("VCO 1 PITCH", "H", "pitch_cents(val)"),
  ("VCO 1 SHAPE", "H"),
  ("VCO 2 WAVE", "B", '["SQR","TRI","SAW"][val]'),
  ("VCO 2 OCTAVE", "B", '["16\'","8\'","4\'","2\'"][val]'),
  ("VCO 2 PITCH", "H", "pitch_cents(val)"),
  ("VCO 2 SHAPE", "H"),
  ("SYNC", "B", "['Off', 'On'][val]"),
  ("RING", "B", "['Off', 'On'][val]"),
  ("CROSS MOD DEPTH", "H"),
  ("MULTI TYPE", "B", "['NOISE','VPM','USER'][val]"),
  ("SELECT NOISE", "B", "['HIGH','LOW','PEAK','DECIM'][val]"),
  ("SELECT VPM", "B","['SIN1','SIN2','SIN3','SIN4','SAW1','SAW2','SQU1','SQU2','FAT1','FAT2','AIR1','AIR2','DECAY1','DECAY2','CREEP','THROAT'][val]"),
  ("SELECT USER", "B", "'USER' + str(val + 1)"),
  ("SHAPE NOISE", "H"),
  ("SHAPE VPM", "H"),
  ("SHAPE USER", "H"),
  ("SHIFT SHAPE NOISE", "H"),
  ("SHIFT SHAPE VPM", "H"),
  ("SHIFT SHAPE USER", "H"),
  ("VCO 1 LEVEL", "H"),
  ("VCO 2 LEVEL", "H"),
  ("MULTI LEVEL", "H"),
  ("CUTOFF", "H"),
  ("RESONANCE", "H"),
  ("CUTOFF DRIVE", "B", '["0%", "50%", "100%"][val]'),
  ("CUTOFF KEYBOARD TRACK", "B", '["0%", "50%", "100%"][val]'),
  ("AMP EG ATTACK", "H"),
  ("AMP EG DECAY", "H"),
  ("AMP EG SUSTAIN", "H"),
  ("AMP EG RELEASE", "H"),
  ("EG ATTACK", "H"),
  ("EG DECAY", "H"),
  ("EG INT", "H", "eg_int(val)"),
  ("EG TARGET", "B", "['CUTOFF', 'PITCH2', 'PITCH'][val]"),
  ("LFO WAVE", "B", '["SQR","TRI","SAW"][val]'),
  ("LFO MODE", "B", "['1-SHOT','NORMAL','BPM'][val]"),
  ("LFO RATE", "H", "lfo_rate(val)"),
  ("LFO INT", "H"),
  ("LFO TARGET", "B", "['CUTOFF', 'SHAPE', 'PITCH'][val]"),
  ("MOD FX ON OFF", "B", "['Off', 'On'][val]"),
  ("MOD FX TYPE", "B", "['CHORUS','ENSEMBLE','PHASER','FLANGER','USER'][val]"),
  ("MOD FX CHORUS", "B", "['STEREO','LIGHT','DEEP','TRIPHASE','HARMONIC','MONO','FEEDBACK','VIBRATO'][val]"),
  ("MOD FX ENSEMBLE", "B", "['STEREO','LIGHT','MONO'][val]"),
  ("MOD FX PHASER", "B", "['STEREO','FAST','ORANGE','SMALL','SMALL RESO','BLACK','FORMANT','TWINKLE'][val]"),
  ("MOD FX FLANGER", "B", "['STEREO','LIGHT','MONO','HIGH SWEEP','MID SWEEP','PAN SWEEP','MONO SWEEP','TRIPHASE'][val]"),
  ("MOD FX USER", "B", "'USER' + str(val + 1)"),
  ("MOD FX TIME", "H"),
  ("MOD FX DEPTH", "H"),
  ("DELAY FX ON OFF", "B", "['Off', 'On'][val]"),
  ("DELAY SUB TYPE", "B", "['STEREO','MONO','PING PONG','HIPASS','TAPE','ONE TAP','STEREO BPM','MONO BPM','PING BPM','HIPASS BPM','TAPE BPM','DOUBLING','USER1','USER2','USER3','USER4','USER5','USER6','USER7','USER8'][val]"),
  ("DELAY TIME", "H"),
  ("DELAY DEPTH", "H"),
  ("REVERB FX ON OFF", "B", "['Off', 'On'][val]"),
  ("REVERB SUB TYPE", "B", "['HALL','SMOOTH','ARENA','PLATE','ROOM','EARLY REF','SPACE','RISER','SUBMARINE','HORROR','USER1','USER2','USER3','USER4','USER5','USER6','USER7','USER8'][val]"),
  ("REVERB TIME", "H"),
  ("REVERB DEPTH", "H"),
  ("X+ BEND RANGE", "B"),
  ("X- BEND RANGE", "B", "-val"),
  ("Y+ ASSIGN", "B", "assign_parameter(val)"),
  ("Y+ RANGE", "B", "str(val-100) + '%'"),
  ("Y- ASSIGN", "B", "assign_parameter(val)"),
  ("Y- RANGE", "B", "str(val-100) + '%'"),
  ("CV IN MODE", "B", "['Modulation','CV/Gate(+)','CV/Gate(-)'][val]"),
  ("CV IN1 ASSIGN", "B", "assign_parameter(val)"),
  ("CV IN1 RANGE", "B", "str(val-100) + '%'"),
  ("CV IN2 ASSIGN", "B", "assign_parameter(val)"),
  ("CV IN2 RANGE", "B", "str(val-100) + '%'"),
  ("MICRO TUNING", "B", "micro_tuning(val)"),
  ("SCALE KEY", "B", "('+' if val > 12 else '') + str(val - 12) + ' Note'"),
  ("PROGRAM TUNING", "B", "('+' if val > 50 else '') + str(val - 50) + ' Cent'"),
  ("LFO KEY SYNC", "B", "['Off', 'On'][val]"),
  ("LFO VOICE SYNC", "B", "['Off', 'On'][val]"),
  ("LFO TARGET OSC", "B", "['ALL','VCO1+VCO2','VCO2','MULTI'][val]"),
  ("CUTOFF VELOCITY", "B"),
  ("AMP VELOCITY", "B"),
  ("MULTI OCTAVE", "B", '["16\'","8\'","4\'","2\'"][val]'),
  ("MULTI ROUTING", "B", "['Pre VCF', 'Post VCF'][val]"),
  ("EG LEGATO", "B", "['Off', 'On'][val]"),
  ("PORTAMENTO MODE", "B", '["Auto","On"][val]'),
  ("PORTAMENTO BPM SYNC", "B", "['Off', 'On'][val]"),
  ("PROGRAM LEVEL", "B", "('+' if val > 102 else '') + '%.1f' % ((float(val)-12)/5 - 18) + 'dB'"),
  ("VPM PARAM1", "B", "str(val-100) + '%'"),
  ("VPM PARAM2", "B", "str(val-100) + '%'"),
  ("VPM PARAM3", "B", "str(val-100) + '%'"),
  ("VPM PARAM4", "B", "str(val-100) + '%'"),
  ("VPM PARAM5", "B", "str(val-100) + '%'"),
  ("VPM PARAM6", "B", "str(val-100) + '%'"),
  ("USER PARAM1", "B", "user_param(val, 1)"),
  ("USER PARAM2", "B", "user_param(val, 1)"),
  ("USER PARAM3", "B", "user_param(val, 1)"),
  ("USER PARAM4", "B", "user_param(val, 1)"),
  ("USER PARAM5", "B", "user_param(val, 1)"),
  ("USER PARAM6", "B", "user_param(val, 1)"),
  ("USER PARAM TYPE", "H"),
  ("PROGRAM TRANSPOSE", "B", "('+' if val > 13 else '') + str(val - 13) + ' Note'"),
  ("DELAY DRY WET", "H"),
  ("REVERB DRY WET", "H"),
  ("MIDI AFTER TOUCH ASSIGN", "B", "assign_parameter(val)"),
  ("PRED", "4s"),
  ("SQ", "2s"), # previously SEQD
  ("Active Step Off/On Steps 1-16","H", "bit_on_off(val) if result[108] == 'SQ' else 'No Active Steps Firmware 1.XX'"),
  ("BPM","H","'%.1f' % (float(val) / 10)"),
  ("Step Length","B"),
  ("Step Resolution","B",'("1/16","1/8","1/4","1/2","1/1")[val]'),
  ("Swing","B", "val-75"),
  ("Default Gate Time","B","str((val * 100) / 72) + '%'"),
  ("Step Off/On Steps 1-16","H", "bit_on_off(val)"),
  ("Step Motion Off/On Steps 1-16","H", "bit_on_off(val)"),
  ("Motion Slot 1 Parameter","H"),
  ("Motion Slot 2 Parameter","H"),
  ("Motion Slot 3 Parameter","H"),
  ("Motion Slot 4 Parameter","H"),
  ("Motion Slot 1 Off/On Steps 1-16","H", "bit_on_off(val)"),
  ("Motion Slot 2 Off/On Steps 1-16","H", "bit_on_off(val)"),
  ("Motion Slot 3 Off/On Steps 1-16","H", "bit_on_off(val)"),
  ("Motion Slot 4 Off/On Steps 1-16","H", "bit_on_off(val)"),
  ("Step 1 Event Data","52s"),
  ("Step 2 Event Data","52s"),
  ("Step 3 Event Data","52s"),
  ("Step 4 Event Data","52s"),
  ("Step 5 Event Data","52s"),
  ("Step 6 Event Data","52s"),
  ("Step 7 Event Data","52s"),
  ("Step 8 Event Data","52s"),
  ("Step 9 Event Data","52s"),
  ("Step 10 Event Data","52s"),
  ("Step 11 Event Data","52s"),
  ("Step 12 Event Data","52s"),
  ("Step 13 Event Data","52s"),
  ("Step 14 Event Data","52s"),
  ("Step 15 Event Data","52s"),
  ("Step 16 Event Data","52s"),
  ("ARP Gate Time","B","str((val * 100) / 72) + '%'"),
  ("ARP Rate","B")
]

motion_parameters = {
    0 : "None",
   15 : "PORTAMENTO",
   16 : "VOICE MODE DEPTH",
   17 : "VOICE MODE TYPE",
   18 : "VCO 1 WAVE",
   19 : "VCO 1 OCTAVE",
   20 : "VCO 1 PITCH",
   21 : "VCO 1 SHAPE",
   22 : "VCO 2 WAVE",
   23 : "VCO 2 OCTAVE",
   24 : "VCO 2 PITCH",
   25 : "VCO 2 SHAPE",
   26 : "SYNC",
   27 : "RING",
   28 : "CROSS MOD DEPTH",
   29 : "MULTI ENGINE TYPE",
   30 : "MULTI ENGINE NOISE TYPE",
   31 : "MULTI ENGINE VPM TYPE",
   33 : "MULTI SHAPE NOISE",
   34 : "MULTI SHAPE VPM",
   35 : "MULTI SHAPE USER",
   36 : "MULTI SHIFT SHAPE NOISE",
   37 : "MULTI SHIFT SHAPE VPM",
   38 : "MULTI SHIFT SHAPE USER",
   39 : "VCO 1 LEVEL",
   40 : "VCO 2 LEVEL",
   41 : "MULTI ENGINE LEVEL",
   42 : "CUTOFF",
   43 : "RESONANCE",
   45 : "KEYTRACK",
   46 : "AMP EG ATTACK",
   47 : "AMP EG DECAY",
   48 : "AMP EG SUSTAIN",
   49 : "AMP EG RELEASE",
   50 : "EG ATTACK",
   51 : "EG DECAY",
   52 : "EG INT",
   53 : "EG TARGET",
   54 : "LFO WAVE",
   55 : "LFO MODE",
   56 : "LFO RATE",
   57 : "LFO INT",
   58 : "LFO TARGET",
   59 : "MOD FX ON/OFF",
   66 : "MOD FX TIME",
   67 : "MOD FX DEPTH",
   68 : "DELAY ON/OFF",
   70 : "DELAY TIME",
   71 : "DELAY DEPTH",
   72 : "REVERB ON/OFF",
   74 : "REVERB TIME",
   75 : "REVERB DEPTH",
  126 : "PITCH BEND",
  129 : "GATE TIME"
}

def user_param(val, i):
  param_type = (result[102] & (3 << (i - 1))) >> (i - 1)

  if param_type == 0: # Percent Type
    return str(val) + '%'

  if param_type == 1: # Bipolar
    return val - 100

  return val # Select

def assign_parameter(val):
  assign_parameters = {
    0 : "GATE TIME",
    1 : "PORTAMENTO",
    2 : "V.M DEPTH",
    3 : "VCO1 PITCH",
    4 : "VCO1 SHAPE",
    5 : "VCO2 PITCH",
    6 : "VCO2 SHAPE",
    7 : "CROSS MOD",
    8 : "MULTI SHAPE",
    9 : "VCO1 LEVEL",
   10 : "VCO2 LEVEL",
   11 : "MULTI LEVEL",
   12 : "CUTOFF",
   13 : "RESONANCE",
   14 : "A.EG ATTACK",
   15 : "A.EG DECAY",
   16 : "A.EG SUSTAIN",
   17 : "A.EG RELEASE",
   18 : "EG ATTACK",
   19 : "EG DECAY",
   20 : "EG INT",
   21 : "LFO RATE",
   22 : "LFO INT",
   23 : "MOD FX SPEED",
   24 : "MOD FX DEPTH",
   25 : "REVERB TIME",
   26 : "REVERB DEPTH",
   27 : "DELAY TIME",
   28 : "DELAY DEPTH"
  }
  return assign_parameters[val]

def micro_tuning(val):
  micro_tuning = {
      0 : "Equal Temp",
      1 : "Pure Major",
      2 : "Pure Minor",
      3 : "Pythagorean",
      4 : "Werckmeister",
      5 : "Kirnburger",
      6 : "Slendro",
      7 : "Pelog",
      8 : "Ionian",
      9 : "Dorian",
    10 : "Aeolian",
    11 : "Major Penta",
    12 : "Minor Penta",
    13 : "Reverse",
    14 : "AFX001",
    15 : "AFX002",
    16 : "AFX003",
    17 : "AFX004",
    18 : "AFX005",
    19 : "AFX006",
    128 : "USER SCALE 1",
    129 : "USER SCALE 2",
    130 : "USER SCALE 3",
    131 : "USER SCALE 4",
    132 : "USER SCALE 5",
    133 : "USER SCALE 6",
    134 : "USER OCTAVE 1",
    135 : "USER OCTAVE 2",
    136 : "USER OCTAVE 3",
    137 : "USER OCTAVE 4",
    138 : "USER OCTAVE 5",
    139 : "USER OCTAVE 6"
  }
  return micro_tuning[val]

def lfo_rate(val):
  if result[44] == 2: # LFO MODE BPM
    if 0 <= val <= 63:
      return 4
    if 64 <= val <= 127:
      return 2
    if 128 <= val <= 191:
      return 1
    if 192 <= val <= 255:
      return 3/4
    if 256 <= val <= 319:
      return 1/2
    if 320 <= val <= 383:
      return 3/8
    if 384 <= val <= 447:
      return 1/3
    if 448 <= val <= 511:
      return 1/4
    if 512 <= val <= 575:
      return 3/16
    if 576 <= val <= 639:
      return 1/6
    if 640 <= val <= 703:
      return 1/8
    if 704 <= val <= 767:
      return 1/12
    if 768 <= val <= 831:
      return 1/16
    if 832 <= val <= 895:
      return 1/24
    if 896 <= val <= 959:
      return 1/32
    if 960 <= val <= 1023:
      return 1/36

  return val

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

def voice_mode_depth(val):
  if result[6] == 1: # ARP
    arp_range = (("0 <= val <= 78", "MANUAL 1"),
      ("79 <= val <= 156", "MANUAL 2"),
      ("157 <= val <=  234", "RISE 1"),
      ("235 <= val <=  312", "RISE 2"),
      ("313 <= val <=  390", "FALL 1"),
      ("391 <= val <=  468", "FALL 2"),
      ("469 <= val <=  546", "RISE FALL 1"),
      ("547 <= val <=  624", "RISE FALL 2"),
      ("625 <= val <=  702", "POLY 1"),
      ("703 <= val <=  780", "POLY 2"),
      ("781 <= val <=  858", "RANDOM 1"),
      ("859 <= val <=  936", "RANDOM 2"),
      ("937 <= val <= 1023", "RANDOM 3"))
    for e in arp_range:
      if eval(e[0]):
        return e[1]

  if result[6] == 2: # UNISON
    return str(val * 50 / 1023) + " Cent"

  if result[6] == 3: # CHORD
    chord_range = (("0 <= val <=  73", "5th"),
    ("74 <= val <= 146", "sus2"),
    ("147 <= val <= 219", "m"),
    ("220 <= val <= 292", "Maj"),
    ("293 <= val <= 365", "sus4"),
    ("366 <= val <= 438", "m7"),
    ("439 <= val <= 511", "7"),
    ("512 <= val <= 585", "7sus4"),
    ("586 <= val <= 658", "Maj7"),
    ("659 <= val <= 731", "aug"),
    ("732 <= val <= 804", "dim"),
    ("805 <= val <= 877", "m7b5"),
    ("878 <= val <= 950", "mMaj7"),
    ("951 <= val <= 1023", "Maj7b5"))
    for e in chord_range:
      if eval(e[0]):
        return e[1]

  if result[6] == 4: # POLY
    return 'Poly' if val < 256 else 'Duo ' + str(val * 50 / 1023)

def pitch_cents(value):
  if 0 <= value <= 4:
    return '-1200C'
  if 4 <= value <= 356: #-1200 ~ -256 (Cent)
    return str((value - 356) * 944 / 352 - 256) + 'C'
  if 356 <= value <= 476: # -256 ~  -16 (Cent)
    return str((value - 476) * 2 - 16) + 'C'
  if 476 <= value <= 492: #  -16 ~   0 (Cent)
    return str(value - 492) + 'C'
  if 492 <= value <= 532: #    0 (Cent)
    return '0C'
  if 532 <= value <= 548: #    0 ~   16 (Cent)
    return str(value - 532) + 'C'
  if 548 <= value <= 668: #   16 ~  256 (Cent)
    return str((value - 548) * 2 + 16) + 'C'
  if 668 <= value <= 1020: #  256 ~ 1200 (Cent)
    return str((value - 668) * 944 / 352 + 256) + 'C'
  if 1020 <= value <= 1023: # 1200 (Cent)
    return '1200C'

def bit_on_off(flags):
  return ("{:016b}".format(flags))[::-1]

def motion_parameter(i):
  return  motion_parameters[i >> 8] + ', Motion ' + ("Off", "On")[i & 1] + ", Smooth " + ("Off", "On")[(i & 2) >> 1]

def step_event_data(data):
  event_structure = [
    ("Note 1", "<B"),
    ("Note 2", "B"),
    ("Note 3", "B"),
    ("Note 4", "B"),
    ("Note 5", "B"),
    ("Note 6", "B"),
    ("Note 7", "B"),
    ("Note 8", "B"),
    ("Velocity 1", "B"),
    ("Velocity 2", "B"),
    ("Velocity 3", "B"),
    ("Velocity 4", "B"),
    ("Velocity 5", "B"),
    ("Velocity 6", "B"),
    ("Velocity 7", "B"),
    ("Velocity 8", "B"),
    ("Gate time 1", "B"),
    ("Gate time 2", "B"),
    ("Gate time 3", "B"),
    ("Gate time 4", "B"),
    ("Gate time 5", "B"),
    ("Gate time 6", "B"),
    ("Gate time 7", "B"),
    ("Gate time 8", "B"),
    ("Motion Slot 1 Data 1", "B"),
    ("Motion Slot 1 Data 2", "B"),
    ("Motion Slot 1 Data 3", "B"),
    ("Motion Slot 1 Data 4", "B"),
    ("Motion Slot 1 Data 5", "B"),
    ("Motion Slot 1 Data 6", "B"),
    ("Motion Slot 1 Data 7", "B"),
    ("Motion Slot 2 Data 1", "B"),
    ("Motion Slot 2 Data 2", "B"),
    ("Motion Slot 2 Data 3", "B"),
    ("Motion Slot 2 Data 4", "B"),
    ("Motion Slot 2 Data 5", "B"),
    ("Motion Slot 2 Data 6", "B"),
    ("Motion Slot 2 Data 7", "B"),
    ("Motion Slot 3 Data 1", "B"),
    ("Motion Slot 3 Data 2", "B"),
    ("Motion Slot 3 Data 3", "B"),
    ("Motion Slot 3 Data 4", "B"),
    ("Motion Slot 3 Data 5", "B"),
    ("Motion Slot 3 Data 6", "B"),
    ("Motion Slot 3 Data 7", "B"),
    ("Motion Slot 4 Data 1", "B"),
    ("Motion Slot 4 Data 2", "B"),
    ("Motion Slot 4 Data 3", "B"),
    ("Motion Slot 4 Data 4", "B"),
    ("Motion Slot 4 Data 5", "B"),
    ("Motion Slot 4 Data 6", "B"),
    ("Motion Slot 4 Data 7", "B"),
  ]
  # get the second value (the unpack structure type field) of all tuples in the list
  # and assemble a unpack structure
  unpackStructure = ''.join(map(lambda x: x[1], event_structure))

  # parse binary using the assembled unpack string
  result = list(struct.unpack(unpackStructure, data))

  result[0] = ("C","C#","D","D#","E","F","F#","G","G#","A","A#", "B")[result[0] % 12] + str(result[0] / 12 - 2)

  if result[4] >= 73:
    result[4] = 'TIE'
  else:
    result[4] = str((result[4] * 100) / 72) + '%'

  return result[0] + ", Velocity " + str(result[2]) + ", Gate time " + result[4]+ "," + str(result[6]) + str(result[7]) + str(result[8]) + str(result[9])


# check one argument is present
if len(sys.argv) != 2 and len(sys.argv) != 3:
  print('Usage: molg.py filename [program number]')
  exit(-1)

programNumber = 0

if len(sys.argv) == 3:
  programNumber = int(sys.argv[2])

# open and read the file
with zipfile.ZipFile(sys.argv[1], mode='r') as file:
  try:
    fileContent = file.read('Prog_%03d.prog_bin'  % (programNumber,))
  except:
    print("Couldn't open file. Check program number and file name.")
    exit(-2)

# get the second value (the unpack structure type field) of all tuples in the list
# and assemble a unpack structure
unpackStructure = ''.join(map(lambda x: x[1], fileStructure))

# parse binary using the assembled unpack string
result = list(struct.unpack(unpackStructure, fileContent))


# print parameters
for i, parameter in enumerate(fileStructure):
  if parameter[0] == "MAGIC" or parameter[0] == "PRED" or parameter[0] == "SQ" or parameter[0] == "END" or parameter[0] == "RESERVED" or parameter[0] == "USER PARAM TYPE":
    # don't print useless fields
    continue

  if parameter[0] == 'Motion Slot 1 Parameter':
    result[i] = motion_parameter(result[i])

  if parameter[0] == 'Motion Slot 2 Parameter':
    result[i] = motion_parameter(result[i])

  if parameter[0] == 'Motion Slot 3 Parameter':
    result[i] = motion_parameter(result[i])

  if parameter[0] == 'Motion Slot 4 Parameter':
    result[i] = motion_parameter(result[i])

  if parameter[0] == "Motion Slot 1 Steps Off/On":
    result[i] = bit_on_off(result[i])

  if parameter[0] == "Motion Slot 2 Steps Off/On":
    result[i] = bit_on_off(result[i])

  if parameter[0] == "Motion Slot 3 Steps Off/On":
    result[i] = bit_on_off(result[i])

  if parameter[0] == "Motion Slot 4 Steps Off/On":
    result[i] = bit_on_off(result[i])

  if parameter[0] == 'Step 1 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 2 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 3 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 4 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 5 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 6 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 7 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 8 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 9 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 10 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 11 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 12 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 13 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 14 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 15 Event Data':
    result[i] = step_event_data(result[i])

  if parameter[0] == 'Step 16 Event Data':
    result[i] = step_event_data(result[i])


  # print parameter
  if len(parameter) < 3: # no transformation necessary
    print(parameter[0] + ': ' + str(result[i]))
  else:
    val = result[i] # make accessing the value from transforms easier
    print(parameter[0] + ': ' + str(eval(parameter[2]))) # transform