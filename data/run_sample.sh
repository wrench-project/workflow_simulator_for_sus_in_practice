#!/bin/bash

../build/workflow_simulator --json_input "$(printf "%s" "$(cat ./sample_input.json)")" --wrench-full-log
