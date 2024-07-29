.data
   float:      .float   456.322
   stringz:    .string  "This is a string"

.text
main:

    li t0, 10
    add t4, t0, t1  # 10+13
    bgt t0, t1, target # if t0 > t1 then target    
    
    # print  last t4
    mv a0, t4
    ecall
   
    # return 
    jr ra

