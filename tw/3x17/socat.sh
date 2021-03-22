#!/bin/sh
socat -v TCP-LISTEN:2323,reuseaddr,fork EXEC:"./3x17"
