#!/bin/bash
# Check Gen8 server specifications for GPU compatibility

echo "=== Gen8 Server Specifications ==="
echo ""

echo "System Information:"
sudo dmidecode -t system | grep -E "(Manufacturer|Product Name|Version)"
echo ""

echo "Chassis Information:"
sudo dmidecode -t chassis | grep -E "(Type|Version)"
echo ""

echo "PCIe Slots:"
sudo dmidecode -t 9 | grep -E "(Slot Designation|Current Usage|Type)" | head -20
echo ""

echo "Power Supply:"
sudo dmidecode -t 39 | grep -A5 "Power Supply" | head -10
echo ""

echo "Current GPU:"
lspci | grep -i vga
echo ""

echo "Available Memory:"
free -h
echo ""

echo "CPU Info:"
lscpu | grep -E "(Model name|CPU\(s\)|Thread\(s\))"
