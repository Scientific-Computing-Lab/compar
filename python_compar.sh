#!/usr/bin/env bash
module load anaconda3
module load intel
module load autopar
module load cetus
module load par4all
sleep 0.2
source $set_p4a_env
/opt/sw/anaconda3/bin/python3 "$@"