# wap to print your name by 1000 times using while loop.

# name = input("Enter your name: ")
# count = 0
# while count < 1000:
#     print(name)
#     count += 1
    
# ---------------------------------------- #

# wap to take a number as input and find the factorial of that number using while loop.

# number = int(input("Enter a number: "))
# factorial = 1
# i = 1
# while i <= number:
#     factorial *= i
#     i += 1
# print("Factorial of", number, "is", factorial)

# ---------------------------------------- #

# wap to add all the element of the above list take input from user using while loop.

# numbers = []
# i = 0
# while i < 5:  
#     num = float(input("Enter a number: "))
#     numbers.append(num)
#     i += 1
# total = sum(numbers)
# print("Sum of all elements:", total)

# ---------------------------------------- #

# wap to add all the element of the above list take input from user using for loop.

# numbers = []
# for i in range(5):
#     num = float(input("Enter a number: "))
#     numbers.append(num)

# # wap to add all the element of the above list using for loop.
# total = 0
# for num in numbers:
#     total += num
# print("Sum of all elements:", total)

# ---------------------------------------- #

# wap to add all the elements of 3's table by using for range loop.Also print Table of 3.
# total = 0
# for i in range(1, 11):
#     total += 3 * i
#     print(f"3 x {i} = {3 * i}")
# print("Sum of all elements in 3's table:", total)

# ---------------------------------------- #

# wap to form a
# 1
# 2 2
# 3 3 3
# 4 4 4 4
# 5 5 5 5 5

# for i in range(1, 6):
#     for j in range(i):
#         print(i, end=" ")
#     print()  
    
# ---------------------------------------- #
    
# wap to form a
# 1
# 1 0
# 1 0 1
# 1 0 1 0
# 1 0 1 0 1

# rows = 5
# for i in range(rows):
#     for j in range(i + 1):
#         if j % 2 == 0:
#             print("1", end=" ")
#         else:
#             print("0", end=" ")
#     print()
        
# ---------------------------------------- #

# Wap to fibonacci series using for loop. 0,1,1,2,3,5,8,...

# n = int(input("Enter the number of terms in the Fibonacci series: "))
# a, b = 0, 1
# for _ in range(n):
#     print(a, end=" ")
#     a, b = b, a + b
    
# # Another way to print Fibonacci series using while loop.
# n = int(input("Enter the number of terms in the Fibonacci series: "))
# a, b = 0, 1
# count = 0
# while count < n:
#     print(a, end=" ")
#     a, b = b, a + b
#     count += 1
    
#---------------------------------------- #

# Functions #
# WAF to check whether a number is palindrome or not using string conversion.

def is_palindrome_math(n):
    if n < 0:
        return False
    
    original = n
    reversed_num = 0

    while n > 0:
        digit = n % 10          
        reversed_num = reversed_num * 10 + digit
        n //= 10                

    return original == reversed_num

num = int(input("Enter a number: "))

if is_palindrome_math(num):
    print(f"{num} is a palindrome.")
else:
    print(f"{num} is not a palindrome.")
