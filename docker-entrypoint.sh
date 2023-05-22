#!/bin/bash
if [ "${WAIT_FOR_SUBGRAPH}" = "true" ]
then
  while [ ! -f "/ocean-subgraph/ready" ]; do
    echo "Waiting for subgraph to be ready...."
    sleep 2
  done
fi
cd /pdr-trader/
echo "Starting app..."
/usr/local/bin/python main.py 2>&1 &
tail -f /dev/null
