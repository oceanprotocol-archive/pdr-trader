#!/bin/bash
if [ "${WAIT_FOR_SUBGRAPH}" = "true" ]
then
  echo "Waiting for subgraph to be ready...."
  while [ ! -f "/ocean-subgraph/ready" ]; do
    sleep 2
  done
fi
cd /pdr-trader/
echo "Delaying startup for ${DELAYED_STARTUP} seconds.."
sleep $DELAYED_STARTUP
echo "Starting app..."
/usr/local/bin/python -u main.py
