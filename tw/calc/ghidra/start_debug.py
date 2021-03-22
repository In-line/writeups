#!/bin/python
import gdb

exec = gdb.execute

gdb.execute("break *eval")

exec("file calc")
exec("run < ../test_input.txt")

# gdb.execute("c")
