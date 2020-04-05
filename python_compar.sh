#!/usr/bin/env bash
module load anaconda3
sleep 0.2
module load intel
sleep 0.2
module load autopar
sleep 0.2
module load cetus
sleep 0.2
module load par4all
sleep 0.2
source $set_p4a_env
sleep 0.2
/opt/sw/anaconda3/bin/python3 "$@"