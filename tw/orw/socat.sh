#!/bin/sh
socat TCP-LISTEN:2323,reuseaddr,fork EXEC:"./orw"
