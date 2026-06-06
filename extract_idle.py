input_file = "csi_com3(2).txt"
output_file = "sit_com3.txt"

with open(input_file, "r", errors="ignore") as fin, \
     open(output_file, "w") as fout:

    count = 0

    for line in fin:

        if "CSI" in line:
            fout.write(line)
            count += 1

    print("Saved rows:", count)