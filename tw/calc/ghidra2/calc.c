#include "calc.h"



void calc(void)

{
  bool iVar1;
  int charactersRead;
  int in_GS_OFFSET;
  InitPool pool;
  char buffer [1024];
  int local_10;
  int canary;
  
  canary = *(int *)(in_GS_OFFSET + 0x14);
  while( true ) {
    bzero(buffer,0x400);
    charactersRead = get_expr(buffer,0x400);
    if (charactersRead == 0) break;
    init_pool(&pool);
    _iVar1 = parse_expr(buffer,&pool);
    if (_iVar1 != 0) {
      printf("%d\n",pool.values[pool.count + -1]);
      fflush((FILE *)stdout);
    }
  }
  if (canary == *(int *)(in_GS_OFFSET + 0x14)) {
    return;
  }
                    // WARNING: Subroutine does not return
  __stack_chk_fail();
}


