# import solcx
# import os
# solcx.install_solc('0.4.25')

import test

test.modify_a()
test.print_a()
test.modify_a()
test.print_a()
test.modify_a()
test.print_a()

b = test.a

b.append(3)

print(b)

test.print_a()
