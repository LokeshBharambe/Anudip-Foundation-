# write a program to take an input and find the possible 200 rupee notes count.

# amount = float(input("Enter the amount: "))
# notes_count = int(amount // 200)
# print("Number of 200 rupee notes =", notes_count)

# ---------------------------------------- #

# write a program to take alphabet as in put and check whether it is vowel or consonant.

# alphabet = input("Enter an alphabet: ").lower()
# if alphabet in ['a', 'e', 'i', 'o', 'u']:
#     print(alphabet, "is a vowel.")
# else:
#     print(alphabet, "is a consonant.")
    
# ---------------------------------------- #

# wap to store 1 to 100 numbers in student.txt file

# with open("student.txt", "w") as file:
#     for number in range(1, 101):
#         file.write(str(number) + "\n")
         
         
# ---------------------------------------- #

# wap to count to take a string as input and show the number of lower case, uppercase

# s = input("Enter a string: ")
# lower = 0
# upper = 0
# for char in s:
#     if char.islower():
#         lower += 1
#     elif char.isupper():
#         upper += 1
# print("Number of lowercase letters:", lower)
# print("Number of uppercase letters:", upper)

# ---------------------------------------- #

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

# wap to take a number as input and check whether it is positive or negative.

# number = float(input("Enter a number: "))
# if number > 0:
#     print("The number is positive.")
# elif number < 0:
#     print("The number is negative.")
# else:
#     print("The number is zero.")

# ---------------------------------------- #

# write a program take input from user as number from 1 to 7 and print the respective week day.

# day = int(input("Enter a number from 1 to 7: "))
# if day == 1:
#     print("Monday")
# elif day == 2:
#     print("Tuesday")
# elif day == 3:
#     print("Wednesday")
# elif day == 4:
#     print("Thursday")
# elif day == 5:
#     print("Friday")
# elif day == 6:
#     print("Saturday")
# elif day == 7:
#     print("Sunday")
# else:
#     print("Invalid input. Please enter a number from 1 to 7.")
    
# ---------------------------------------- #

# write a program to take input amount as input and calculate the total payable tax. 
# Tax rates are : 
# 0-3 lac - 0%, 
# 3-5 lac - 5%, 
# 5-12 lac - 10%, 
# above 12 lac - 15%.

amount = float(input("Enter the amount: "))
if amount <= 300000:
     tax = 0
elif amount <= 500000:
     tax = (amount - 300000) * 0.05
elif amount <= 1200000:
     tax = 10000 + (amount - 500000) * 0.1
else:
 tax = 80000 + (amount - 1200000) * 0.15

print("Total payable tax:", tax)

# ---------------------------------------- #

