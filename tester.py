
##### TEST PARSE #####
def testparse(str):
        # shall return list of instructions
        # example: "d-A3-l d-C3-u g-E1-u"
        # [("d", "A3", "l"), ("d", "C3", "u"), ("g", "E1", "u")]
        ans = []
        insts = str.split()
        for i in insts:
            parts = i.split("-")
            ans.append(tuple(parts))

        return ans


parse1 = testparse("d-A3-l d-C3-u g-E1-u")

print(parse1)