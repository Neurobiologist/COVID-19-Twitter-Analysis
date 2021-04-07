total = 0

with open('jan_sub_count.txt', 'r') as inp:
    for line in inp:
        num = float(line)
        total += num

print(total)
