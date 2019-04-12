# MESIWriteBack
Structure : Processing unit contains four cores and four memory blocks where each cache of core can hold one memory location.

Input : 
Program accepts input from user. 
Instuction Type : 
	0 : read
	1 : write
Instruction format-> for
          write: processor_no,value,memory_block
          read:  processor_no,memory_block

For example,
Write Instruction ->

	Processor 0 writes 23 at memory block 2
	Instruction type : 1
	Instuction format : 0,23,2


Read Instruciton ->

	Processor 0 reads from memory block 2
	Instruction type : 0
	Instuction format : 0,2

How to run :
download and run under python shell

