.text
main:
  addi t0, t1, imm; # t0 = t1 + imm
  beq t1, t2, end1      # if(t1 == t2) --> jump to fin1
  jr ra
