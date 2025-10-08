#!/bin/bash
echo "Starting entrypoint script..."
if [ -z "$1" ] ; then
    echo "Usage: $0 {python}"
    echo " Usage : $1 {help | test}"
    exit 1
elif [ "$1" = "help" ] ; then
    echo "This is an automated test script for unit tests."
    echo "Usage : $0 {python}"
    echo "Usage : $1 {test}"
    echo "Example : python test"
    exit 0
elif [ "$1" = "test" ] ; then
    echo "Running unit tests..."
    echo "Maximize Windows screen for better visibility."
    sleep 5
    . OpenCtrlEnv/Scripts/activate
    python -m controls.test
    echo "Unit tests completed."
    exit 0
else
    echo "Invalid argument: $1"
    echo "Usage: $0 {python}"
    echo " Usage : $1 {help | test}"
    exit 1
fi
