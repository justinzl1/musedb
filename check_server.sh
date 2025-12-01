#!/bin/bash

# Supabase Server Connectivity Check Script
# This script checks if the Supabase database server is accepting connections

echo "Checking Supabase server connectivity..."
echo "Host: aws-1-us-east-2.pooler.supabase.com"
echo "Port: 5432"
echo ""

# Check if netcat is available
if ! command -v nc &> /dev/null; then
    echo "Error: netcat (nc) is not installed or not in PATH"
    echo "Please install netcat to use this script"
    exit 1
fi

# Test the connection
echo "Testing connection..."
if nc -vz aws-1-us-east-2.pooler.supabase.com 5432; then
    echo ""
    echo "SUCCESS: Server is up and accepting connections!"
    echo "The database server is reachable and the port is open."
else
    echo ""
    echo "FAILED: Server is not responding"
    echo ""
    echo "Possible reasons:"
    echo "1. Database is paused (check Supabase dashboard)"
    echo "2. Server is down for maintenance"
    echo "3. Network connectivity issues"
    echo "4. Firewall blocking the connection"
    echo "5. Incorrect hostname or port"
    echo ""
    echo "Next steps:"
    echo "- Check your Supabase dashboard"
    echo "- Verify the database is active"
    echo "- Check for any maintenance notifications"
fi
