'''
This conf tests the independent handling of speakers. The aim is to handle seperetly the two speakers either 
by using different tone_freq or tone_pulse_freq or tone_volume. 
'''
from Experiments.MatchPort import *
from Behaviors.MultiPort import *
from Stimuli.test_Tones_Panda_Speakers import *
from scipy import interpolate