#!/usr/bin/python


######################################
#gather AJAX data

import sys, json
  
obj = json.load(sys.stdin)

cues = []
letters = []   

for i in obj["intervals"]: cues.append(i)
for l in obj["letters"]: letters.append(l)

print 'Content-Type: text/html;charset=utf-8'


#
######################################


import wave, audioop, binascii, struct
# 
# TODO:
# 
# CYCLING MIXING OF NEW SAMPLES INTO EXISTING BUFFER
# ALGO:
# 
# IF CUE(N+1)>CUE(N)+LEN(N) -> ADD SILENCE(INTERVAL-LEN(N)) -> ADD NEW LETTER
# IF CUE(N+1)>CUE(N)+LEN(N) <= MIX(BUFFER, NEW_LETTER_SOUND, OFFSET, SRATE)
#
#
######################################
#

sample, frames = [], []

i = 0

samples_dict = {}

for l in list(map(chr, range(97, 102))):
	wav = wave.open('../data/samples/' + l + '.wav','r')
	sample.append(wav)
	# get smp1 data
	(nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
	frames = nframes * nchannels
	samples_data = sample[i].readframes(frames)
	samples_dict[l] = samples_data
#	buff.append(sample[i].readframes(frames))
	#
	i += 1
	
_bits = sample[0].getsampwidth()
srate = sample[0].getframerate()
#sample[0].getframerate()

#
######################################




######################################
# initial setup

bits = 24
max_smp_val = 16777215

mixing_buffer = ""

######################################


######################################
# functions

def silence(samples, smp_rate, bits=16):
	""" Generate n samples of silence
	""" 
	silence_region = "\x00"*samples
	return silence_region
	
def ms_to_samps(ms, smp_rate):
	""" Convert milliseconds to samples
	""" 
	return 3*int(smp_rate*ms / 1000.)
	
def samps_to_ms(samps, smp_rate):
	""" Convert milliseconds to samples
	""" 
	return 1000*int(samps / (3*smp_rate))	
	
# def offset_in_samples(ms, smp_rate, bits=24, _channels=2):
# 	return ms_to_samps(ms, smp_rate) * (bits / 8) * _channels

def mix(buffer, sound, offset, srate):
	""" Mix new sound with WAVE buffer starting from crosspoint cue
		offset: offset from end of mixing buffer in samples
	"""
	
#	o = offset_in_samples(offset, srate, bits)
#	buff_sample_1 = sound_a_ba[o:(o + len(sound_b_ba))]
	
	mix = []
	
	mb_mix_cue = len(buffer) - offset 
		
	for i in range(0, len(sound), 3):
		cue = mb_mix_cue + i
		try:
			smp_a_int = wave_sample_int(buffer[cue:(cue + 3)]) 
		except:
 			smp_a_int = 0			
		smp_b_int = wave_sample_int(sound[i:i + 3])
		sum = smp_a_int + smp_b_int
		if (sum > max_smp_val):
			sum = max_smp_val
		hex = format(smp_b_int,'x')
		hex = "0"*(6 - len(hex)) + hex
		bytes = hextranslate(hex)
		mix.append(bytes[::-1])
	
	return mix
		
		#buffer[:cue+3].replace(buffer[cue:cue+3],chrs) + buffer[cue+3:]
		
#	for s1 in sound1[buff_sample_1:]:
#		mixing_buffer.append()
	pass
	
def hextranslate(s):
        res = ""
        for i in range(len(s)/2):
                realIdx = i*2
                res = res + chr(int(s[realIdx:realIdx+2],16))
        return res	
	
def to_bytes(n, length, endianess='big'):
    h = '%x' % n
    s = ('0'*(len(h) % 3) + h).zfill(length*2).decode('hex')
    return s if endianess == 'big' else s[::-1] 
	
def convert(int_value):
    encoded = format(int_value, 'x')

    length = 3
    encoded = encoded.zfill(length+length%2)

    return encoded.decode('hex')	
	
def wave_sample_int(smpl_bytes_array): 
	"""
		Convert little endian sample bytes array to integer
	"""
#	print ord(smpl_bytes_array[2])
	return int(smpl_bytes_array[::-1].encode("hex"),16)	
		
	
######################################



######################################
# generate blank silence wave

blank_wave = silence(660, srate, 24)

######################################


#print int_to_little_endian_bytes(1345)


output = wave.open('../data/mix3new.wav','w')

# set output WAVE format
#output.setnchannels(1)
#output.setsampwidth(_bits)
#output.setframerate(
output.setparams((1, _bits, srate, 0, 'NONE', 'not compressed'))

mixing_buffer += blank_wave
a = ""
prev_sound_len = 0

for i in range(0,len(letters)):
	samples_data = samples_dict[letters[i]]
	offset = ms_to_samps(cues[i], srate)

	delta = offset - prev_sound_len

	if (delta >= 0) :
		mixing_buffer += silence(delta, srate, 24)
		mixing_buffer += samples_data
		a += "<p>added silence</p>"
		print "added silence"
	else:
		print "mixed"
		mixed_region = mix(mixing_buffer, samples_data, abs(delta), srate)
		value_str = ''.join(mixed_region)
		x = len(mixing_buffer) - abs(delta)
		a += "<p>mixed</p>"
		mixing_buffer = mixing_buffer[:x] + value_str
		
	prev_sound_len = len(samples_data)

value_str = ''.join(mixing_buffer)
output.writeframes(value_str)
output.close()

# print json.dumps(a)

#	TODO
#	function generate_silence(ms)
#	function mix(sound1, sound2, offset)
#
