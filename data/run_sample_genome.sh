#!/bin/bash

# Genome
../build/workflow_simulator --json_input "$(printf "%s" "$(cat ./sample_input_genome.json)")" --wrench-full-log
