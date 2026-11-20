#!/bin/bash
for i in {1..60}
do
  status=$(curl -s -o /dev/null -w "%{http_code}" http://emi.local/api/history)
  if [ "$status" -eq 200 ]; then
    echo "Request $i: SUCCESS ($status)"
  else
    echo "Request $i: FAILED ($status)"
  fi
  sleep 1
done
