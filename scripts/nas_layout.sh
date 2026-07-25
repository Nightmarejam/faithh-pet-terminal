#!/bin/bash
ssh nas 'find /volume1 -maxdepth 4 -type d | grep -v "/@" | grep -v "/#recycle" | sort'
