#!/bin/bash

echo "=== HOSTNAMECTL ==="
hostnamectl

echo "=== OS_RELEASE ==="
cat /etc/os-release

echo "=== IP_ROUTE_GET ==="
ip route get 1.1.1.1

echo "=== UPTIME_PRETTY ==="
uptime -p

echo "=== LOADAVG ==="
cat /proc/loadavg

echo "=== CPU_TEMP ==="
cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "unavailable"

echo "=== MEMORY_FREE_B ==="
free -b

echo "=== DISK_ROOT_B ==="
df -B1 --output=source,size,used,avail,pcent,target /

echo "=== NETWORK_DEV ==="
cat /proc/net/dev

echo "=== CPU_CORES ==="
nproc