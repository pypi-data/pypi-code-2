# GoldenRatio - having fun with the Fibonnacci number sequence
#
#

bignum = int(input('What is the largest Fibbonacci number for this run? '))

def Fibonnacci(biggest, a = 1, b = 2):
   """ Calculates the Golden Ratio given a highest Fibonnacci number nearest to input number
       For example: If biggest is 58, then the Golden Ratio is 55/89
   """
   Fib = a + b

   while Fib < biggest:
      a = b
      b = Fib
      Fib = a + b
      print (Fib, b/Fib, sep =' ')
      global ratio
      ratio = b/Fib
   return(ratio)

golden = Fibonnacci(bignum)






   


    
