#!/bin/bash

echo "Checking Supabase server connectivity..."

if ! command -v nc &> /dev/null; then
    echo "Error: netcat (nc) is not installed or not in PATH"
fi

echo "Testing connection..."
if nc -vz aws-1-us-east-2.pooler.supabase.com 5432; then
    echo "SUCCESS: Server is up and accepting connections!"
else
    echo "FAILED: Server is not responding"  
fi
