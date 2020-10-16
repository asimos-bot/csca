#!/usr/bin/env python3
import sys

if( len(sys.argv) != 2 ):
    print("Expected use: python3 crack.py <Order of Square-Reduce-Multiply detections>")

binary = sys.argv[1].replace("SM", '1').replace("S", '0')

print(binary)
