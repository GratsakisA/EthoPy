from Experiments.MatchPort import *
from Stimuli.Tones_Grating import *
from Behaviors.MultiPort import *

def _get_new_cond_f(self):
    if self.curr_cond['trial_selection'] == 'staircase':
        perf, choice_h = self._get_performance()
        if np.size(self.beh.choice_history) and self.beh.choice_history[-1:][0] > 0:
            self.cur_block_sz += 1  
        if self.cur_block_sz >= self.curr_cond['staircase_window']:
            if perf >= self.curr_cond['stair_up']:
                self.cur_block = self.curr_cond['next_up']
                self.cur_block_sz = 0
                self.logger.update_setup_info({'difficulty': self.cur_block})
            elif perf < self.curr_cond['stair_down']:
                self.cur_block = self.curr_cond['next_down']
                self.cur_block_sz = 0
                self.logger.update_setup_info({'difficulty': self.cur_block})
        if self.curr_cond['antibias']:
            anti_bias = self._anti_bias(choice_h, self.un_choices[self.un_blocks == self.cur_block])
            condition_idx = np.logical_and(self.choices == anti_bias, self.blocks == self.cur_block)
        else: condition_idx = self.blocks == self.cur_block
        # Do not repeat condition if it was the last trial of the block
        if self.curr_cond['repeat_trial'] and self.cur_block_sz:
            if np.size(self.beh.choice_history) and self.beh.choice_history[-1:][0] > 0:
                if ~np.isnan(self.beh.punish_history[-1]): self.repeat_trial=1
                else: self.repeat_trial=0
            if self.repeat_trial:
                self.block_h.append(self.cur_block)
                return
        self.curr_cond = np.random.choice([i for (i, v) in zip(self.conditions, condition_idx) if v])
        self.block_h.append(self.cur_block)
@dataclass
class Block_f:
    difficulty: int = field(compare=True, default=0, hash=True)
    stair_up: float = field(compare=False, default=.7)
    stair_down: float = field(compare=False, default=0.55)
    next_up: int = field(compare=False, default=0)
    next_down: int = field(compare=False, default=0)
    staircase_window: int = field(compare=False, default=20)
    bias_window: int = field(compare=False, default=5)
    trial_selection: str = field(compare=False, default='fixed')
    metric: str = field(compare=False, default='accuracy')
    antibias: bool = field(compare=False, default=True)
    noresponse_intertrial: bool = field(compare=False, default=True)
    incremental_punishment: bool = field(compare=False, default=False)
    repeat_trial: bool = field(compare=False, default=False)
    def dict(self):
        return self.__dict__


###-------------------------------------------------------Experiment configuration
# define session parameters
session_params = {
    'max_reward'         : 1200,
    'min_reward'         : 50, 
    'setup_conf_idx'     : 9,
}

exp = Experiment()
exp.setup(logger, MultiPort, session_params)
ExperimentClass._get_new_cond=_get_new_cond_f
exp.Block=Block_f     
exp.repeat_trial=0

# define stimulus and other trial parameters
key = {
    #Grating
    'spatial_freq'        : .05,   # cycles/deg
    'square'              : 0,     # squarewave or Guassian
    'temporal_freq'       : 0,     # cycles/sec
    'flatness_correction' : 1,     # adjustment of spatiotemporal frequencies based on animal distance
    'duration'            : 5000,
    #Tones
    'tone_duration'       : 5000,   
    'tone_frequency'      : 40500,      #hz 
    #Trial parameters
    'punish_duration'     : 8000,  # target: 8000
    'abort_duration'      : 500,
    'init_ready'          : 10,
    'trial_ready'         : 50, 
    'trial_duration'      : 5000, 
    'intertrial_duration' : 2000,
    'reward_duration'     : 2000,
    'reward_amount'       : 5,
}

stim= Tones_Grating()
stim.fill_colors.set({'background': (0, 0, 0),
                           'start': (0.2, 0.2, 0.2),
                           'ready': (0.3, 0.3, 0.3),
                           'reward': (0.6, 0.6, 0.6),
                           'punish': (0, 0, 0)})
conditions = []

theta    = [0,  90]
tn_freq  = [0, 100]    
rew_prob = [1,   2] 

block=exp.Block(difficulty=1, next_down=1, next_up=2, trial_selection='staircase', staircase_window=40, stair_down=0, stair_up=0, antibias=False, bias_window=5, repeat_trial=True)
for idx in range(len(rew_prob)): 
    conditions += exp.make_conditions(stim_class=stim, conditions={**block.dict(), **key,                                                                     
    'theta'             : theta[idx],
    'tone_pulse_freq'   : tn_freq[idx],
    'tone_volume'       : 0,  
    'contrast'          : 80,
    'reward_port'       : rew_prob[idx],
    'response_port'     : rew_prob[idx]})


block=exp.Block(difficulty=2, next_down=2, next_up=1, trial_selection='staircase', staircase_window=40, stair_down=0, stair_up=0, antibias=False, bias_window=5, repeat_trial=True)
for idx in range(len(rew_prob)): 
    conditions += exp.make_conditions(stim_class=stim, conditions={**block.dict(), **key,                                                                     
    'theta'             : theta[idx],
    'tone_pulse_freq'   : tn_freq[idx],
    'tone_volume'       : 45,  
    'contrast'          : 0,
    'reward_port'       : rew_prob[idx],
    'response_port'     : rew_prob[idx]})

np.random.seed()
# run experiments
exp.push_conditions(conditions)
exp.start()