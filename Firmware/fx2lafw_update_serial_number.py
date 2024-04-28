#!/usr/bin/env python3

import re
import pathlib
import sys

serno_descriptor_file = pathlib.Path("sigrok-firmware-fx2lafw") / "hw" / "sigrok-fx2-8ch" / "dscr.a51"

DESCRIPTOR_LINE_REGEX = re.compile(r'string_descriptor_a 3,\^\"([^"]+)\"')

if len(sys.argv) != 2:
    print(f"Error: Usage: {sys.argv[0]} <serial number of board>")
    sys.exit(1)

try:
    int(sys.argv[1])
except ValueError:
    print("Serial number argument must be an integer")
    sys.exit(1)

descriptor_file_text = serno_descriptor_file.read_text()
search_result = re.search(DESCRIPTOR_LINE_REGEX, descriptor_file_text)
if search_result is None:
    print("Can't fine target line in descriptor file")
    sys.exit(1)
else:
    print("Old serial number: " + search_result.group(1))

new_serial_number = "Mbed CE CI FX2LAFW SN" + sys.argv[1]
print("New serial number: " + new_serial_number)

new_descriptor_line = 'string_descriptor_a 3,^"' + new_serial_number + '"'

new_file_text = re.sub(DESCRIPTOR_LINE_REGEX, new_descriptor_line, descriptor_file_text)
serno_descriptor_file.write_text(new_file_text)