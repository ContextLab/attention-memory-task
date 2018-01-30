#!/usr/bin/env python

import sys
from os import chdir
from subprocess import call
from os.path import exists, join
import numpy as np
from mvpa2.base.hdf5 import h5save

if len(sys.argv) > 1:
    participant = sys.argv[1]
else:
    participant = 99
    print("Generating timing for test participant 99")

timing_dir = '/home/nastase/social_actions/scripts/timing'
sim_dir = join(timing_dir, 'timing_sim_{0}'.format(participant))

chdir(timing_dir)

# Run AFNI's @stim_analyze to generate randomized onsets
if not exists(sim_dir):
    call('@stim_analyze {0}'.format(participant), shell=True)
elif exists(sim_dir):
    print("Simulations already exist for participant {0}".format(participant))

call('sort -n timing_sim_{0}/NSD_sums | head -1'.format(
        participant), shell=True)

# Get iteration lowest normalized standard devation
with open(join(sim_dir, 'NSD_sums')) as f:
    nsd = {float(line.split()[0]): line.split()[5] for line in f.readlines()}

min_iter = nsd[min(nsd)].strip(',')
print("Minimum normalized standard deviation = {0} "
      "at iteration {1} for participant {2}".format(
        min(nsd), min_iter, participant))

# Print summary file
with open(join(sim_dir, 'out.mrt.{0}'.format(min_iter))) as f:
    print(f.read())

# Get timing
with open(join(sim_dir, 'stimes.{0}_01_trial.1D'.format(min_iter))) as f:
    timing = np.array([[float(onset) for onset in line.split()] for line in f.readlines()])

assert timing.shape == (8, 103)

h5save(join(timing_dir, 'timing_final_{0}.hdf5'.format(participant)), timing)
