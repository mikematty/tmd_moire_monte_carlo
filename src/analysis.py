import numpy as np
import matplotlib.pyplot as plt
import os
import re
import pickle
from operators import *

# parses a filename for a saved operator file generated by particle_mc.py
# ARGS:
#   fname <- filename string formatted such as those generated by particle_mc
# RETURNS:
#   a dictionary mapping strings to simulated parameter values
def parse(fname):
  # parse file name with regular expression below
  parser = re.compile(r'\d+[.]?\d*')
  params = parser.findall(fname)
  # system size, filling numerator, filling denominator, temperature keys
  param_names = ['l','num','denom','temp']
  param_dict = {}
  assert(len(params) == len(param_names))
  # build dictionary of parameters
  for i in range(len(params)):
    p = params[i]
    if '.' in p: p = float(p)
    else: p = int(p)
    param_dict[param_names[i]] = p
  return param_dict

# load lattice configurations produced by simulation
# ARGS:
#   prefix <- string corresponding to beginning of saved parameter file
#   fixed_l <- integer corresponding to lattice size to load data from
# RETURNS:
#   array of tuples with parameters at index 0 and lattice configs at index 1
def load_configs(prefix,fixed_l):
  res = []
  # temperature scaling factor based on Veit, Fai, and Jie's paper
  t_factor=((1.60217e-19)**2/(4*np.pi*8.85418782e-12*3.9*8e-9))/(1.380649e-23)
  #for f in filter(lambda x: ".npy" in x, os.listdir("saved_configs/")):
  for f in filter(lambda x: x.startswith(prefix), os.listdir("saved_configs/")):
    params = parse(f[len(prefix):])
    if params['l'] != fixed_l: continue
    #params['temp'] *= t_factor
    lats = np.load("saved_configs/"+f)
    res += [(params,lats)]
  return res

def main(eval_nop=True,eval_sf=False):
  prefix = "300321b" 
  #prefix = "160321a"
  #prefix = "220321a"
  fixed_l = 20
  data = load_configs(prefix,fixed_l)
  res = []
  sf = StructureFactor(fixed_l,sum_evals=True)
  for (params,configs) in data:
    """
    t = 0.001 #np.linspace(0.001,0.08,20)[4]
    num = 152
    if (params['num'] != num): continue
    if not np.allclose(params['temp'],t): continue
    if (params['num'] == num) and np.allclose(params['temp'],t):
      #for i in range(1): print(list(configs[i,:]))
      c_index = 50
      nop = NematicOP(params['l'],sum_evals=False,spatial_average=True)
      nop.evaluate(configs[c_index,:])
      tmp = np.arctan2(nop.state[1,-1],nop.state[0,-1])/2
      if tmp < 0: tmp += np.pi
      tmp *= 180/np.pi
      print(tmp)
      print(list(configs[c_index,:]))
      #sf = StructureFactor(fixed_l)
      #sf.evaluate(configs[c_index,:])
      #np.save("sf",sf.state)
    return
    """
    nop = NematicOP(params['l'],sum_evals=False,spatial_average=True)
    #nrg = Energy(params['l'],sum_evals=False)
    for i in range(0,configs.shape[0]):
      #nrg.evaluate(configs[i,:])
      nop.evaluate(configs[i,:])
      tmp = np.arctan2(nop.state[1,-1],nop.state[0,-1])/2
      if tmp < 0: tmp += np.pi
      tmp *= 180/np.pi
      if np.allclose(tmp,0) or np.allclose(tmp,0):
        sf.evaluate(configs[i,:])
    nop_tensor = np.array([[np.mean(nop.state[0,:]*nop.state[0,:]),\
                            np.mean(nop.state[0,:]*nop.state[1,:])],\
                           [np.mean(nop.state[1,:]*nop.state[0,:]),\
                            np.mean(nop.state[1,:]*nop.state[1,:])]])
    nop_sq = np.mean(np.square(nop.state[0,:])+np.square(nop.state[1,:]))
    theta = np.arctan2(nop.state[1,:],nop.state[0,:])/2
    theta[theta < 0] += np.pi
    theta = theta*180/np.pi
    #nrg_avg = np.mean(nrg.state)
    #nrg_sq_avg = np.mean(nrg.state*nrg.state)
    #specific_heat = nrg_sq_avg - nrg_avg*nrg_avg
    
    #res += [(params, nop_sq, sf.state)]
    res += [(params, nop_sq, sf.state/sf.n_evals, [], [],nop_tensor,theta)]#nrg_avg, specific_heat)]
    sf.reset()
    #print(params)
  pickle.dump(res, open('out.p','wb'))
  return res

if __name__ == '__main__': main()