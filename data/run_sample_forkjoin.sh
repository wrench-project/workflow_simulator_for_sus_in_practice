#!/bin/bash

# Forkjoin
../build/workflow_simulator --json_input "$(printf "%s" "$(cat ./sample_input_forkjoin.json)")" --wrench-full-log
