#/usr/bin/python

input_name = "./input.text"
input = open(input_name,'r').read().splitlines()

output_a = open("%sa" % (input_name), 'w')
output_b = open("%sb" % (input_name), 'w')

for line in input:
    if ("INGV " in line):
        output_a.write(line + '\n')
    else:
        output_b.write(line + '\n')