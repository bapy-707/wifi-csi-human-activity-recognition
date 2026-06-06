with open("csi_com4.txt") as f:
    lines = f.readlines()

total = len(lines)
print("Total lines:", total)

part = total // 3

idle = lines[0:part]
walk = lines[part:2*part]
sit  = lines[2*part:]

# Save files
with open("idle_2.txt", "w") as f:
    f.writelines(idle)

with open("walk_2.txt", "w") as f:
    f.writelines(walk)

with open("sit_2.txt", "w") as f:
    f.writelines(sit)

print(" Data split into idle, walk, sit")