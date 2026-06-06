input_file = "csi_com4(2).txt"
output_file = "idle_com4.txt"

with open(input_file, "r", errors="ignore") as fin, \
     open(output_file, "w") as fout:

    count = 0

    for line in fin:

        if "CSI" in line:
            fout.write(line)
            count += 1

    print("Saved rows:", count)