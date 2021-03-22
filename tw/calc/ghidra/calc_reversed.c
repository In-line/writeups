#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>

typedef struct Pool Pool, *PPool;

struct Pool {
    int count;
    int values[100];
};

void calc(void);
void timeout(void);
int get_expr(char *buffer,size_t maxLen);
void eval(Pool *pool,char operator);
void init_pool(Pool *pool);
int parse_expr(char *buffer,Pool *pool);


void calc(void)
{
  int iVar2;
  int iVar1;
  // int in_GS_OFFSET;
  Pool pool;
  char buffer [1024];
  // int canary;
  
  // canary = *(int *)(in_GS_OFFSET + 0x14);
  while( true ) {
    bzero(buffer,0x400);
    iVar2 = get_expr(buffer,0x400);
    if (iVar2 == 0) break;
    init_pool(&pool);
    iVar1 = parse_expr(buffer,&pool);
    if (iVar1 != 0) {
      printf("%d\n",pool.values[pool.count + -1]);
      fflush((FILE *)stdout);
    }
  }
//   if (canary == *(int *)(in_GS_OFFSET + 0x14)) {
//     return;
//   }
                    // WARNING: Subroutine does not return
  // __stack_chk_fail();
}

void timeout(void)
{
  puts("No time to waste!");
  exit(0);
}

int get_expr(char *buffer,size_t maxLen)
{
  ssize_t numberOfBytesRead;
  char currentCharacter;
  int i;
  
  i = 0;
  while (i < (int)maxLen) {
    numberOfBytesRead = read(0,&currentCharacter,1);
    if ((numberOfBytesRead == -1) || (currentCharacter == '\n')) break;
    if ((((currentCharacter == '+') ||
         (((currentCharacter == '-' || (currentCharacter == '*')) || (currentCharacter == '/')))) ||
        (currentCharacter == '%')) || (('/' < currentCharacter && (currentCharacter < ':')))) {
      buffer[i] = currentCharacter;
      i = i + 1;
    }
  }
  buffer[i] = '\0';
  return i;
}

void eval(Pool *pool,char operator)
{
  if (operator == '+') {
    printf("a+=b, a = %x, b = %x\n", pool->values[pool->count + -2], pool->values[pool->count + -1]);
    pool->values[pool->count + -2] =
         pool->values[pool->count + -2] + pool->values[pool->count + -1];
    printf("Pool count: %x, address %x\n", pool->count, &pool->values[pool->count - 2]); 
  }
  else {
    if (operator < ',') {
      if (operator == '*') {
        pool->values[pool->count + -2] =
             pool->values[pool->count + -2] * pool->values[pool->count + -1];
      }
    }
    else {
      if (operator == '-') {
        pool->values[pool->count + -2] =
             pool->values[pool->count + -2] - pool->values[pool->count + -1];
      }
      else {
        if (operator == '/') {
          pool->values[pool->count + -2] =
               pool->values[pool->count + -2] / pool->values[pool->count + -1];
        }
      }
    }
  }
  pool->count = pool->count + -1;
  return;
}

void init_pool(Pool *pool)
{
  int i;
  
  pool->count = 0;
  i = 0;
  while (i < 100) {
    pool->values[i] = 0;
    i += 1;
  }
  return;
}



int parse_expr(char *buffer,Pool *pool)
{
  char *currentNumberString;
  int isNumberNotZero;
  int returnValue;
  int currentNumber;
  size_t lengthOfCurrentNumber;
  // int in_GS_OFFSET;
  char *currentBufferPosPtr;
  int i;
  int operatorIndex;
  char currentBuffer [100];
  int local_10;
  //int canary;
  int insertIndex;
  
  // canary = *(int *)(in_GS_OFFSET + 0x14);
  currentBufferPosPtr = buffer;
  operatorIndex = 0;
  bzero(currentBuffer,100);
  i = 0;
  do {
    if (9 < (int)buffer[i] - 0x30U) {
      lengthOfCurrentNumber = (size_t)(buffer + (i - (int)currentBufferPosPtr));
      currentNumberString = (char *)malloc(lengthOfCurrentNumber + 1);
      memcpy(currentNumberString,currentBufferPosPtr,lengthOfCurrentNumber);
      currentNumberString[lengthOfCurrentNumber] = '\0';
      isNumberNotZero = strcmp(currentNumberString,"0");
      if (isNumberNotZero == 0) {
        puts("prevent division by zero");
        fflush((FILE *)stdout);
        returnValue = 0;
        goto LAB_0804935f;
      }
      currentNumber = atoi(currentNumberString);
      if (0 < currentNumber) {
        insertIndex = pool->count;
        pool->count = insertIndex + 1;
        pool->values[insertIndex] = currentNumber;
      }
      if ((buffer[i] != '\0') && (9 < (int)buffer[i + 1] - 0x30U)) {
        puts("expression error!");
        fflush((FILE *)stdout);
        returnValue = 0;
        goto LAB_0804935f;
      }
      currentBufferPosPtr = buffer + i + 1;
      if (currentBuffer[operatorIndex] == '\0') {
        currentBuffer[operatorIndex] = buffer[i];
      }
      else {
        switch(buffer[i]) {
        case '%':
        case '*':
        case '/':
          if ((currentBuffer[operatorIndex] == '+') || (currentBuffer[operatorIndex] == '-')) {
            currentBuffer[operatorIndex + 1] = buffer[i];
            operatorIndex = operatorIndex + 1;
          }
          else {
            eval(pool,currentBuffer[operatorIndex]);
            currentBuffer[operatorIndex] = buffer[i];
          }
          break;
        default:
          eval(pool,currentBuffer[operatorIndex]);
          operatorIndex = operatorIndex + -1;
          break;
        case '+':
        case '-':
          eval(pool,currentBuffer[operatorIndex]);
          currentBuffer[operatorIndex] = buffer[i];
        }
      }
      if (buffer[i] == '\0') {
        while (-1 < operatorIndex) {
          eval(pool,currentBuffer[operatorIndex]);
          operatorIndex += -1;
        }
        returnValue = 1;
LAB_0804935f:
        // if (canary != *(int *)(in_GS_OFFSET + 0x14)) {
        //             // WARNING: Subroutine does not return
        //   __stack_chk_fail();
        // }
        return returnValue;
      }
    }
    i += 1;
  } while( true );
}

void main(void)

{
  signal(0xe,timeout);
#if 0
  alarm(0x3c);
#endif
  puts("=== Welcome to SECPROG calculator ===");
  fflush((FILE *)stdout);
  calc();
  puts("Merry Christmas!");
  return;
}
