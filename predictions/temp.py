number = [0,0,0,0,0,0]
# increment number by 1 as a full number
until = 20

def plusOne(number, idx):
    if idx == -1 or idx > len(number) - 1:
        return
    number[idx] += 1
    if number[idx] == 10:
        number[idx] = 0
        plusOne(number, idx - 1)

def incrementNumber(number, until, idx):
    if idx == -1 or idx > len(number) - 1:
        return
    while until > 0:
        plusOne(number, idx)
        print(number)
        until -= 1
    return number

print(incrementNumber(number, until, len(number) - 1))