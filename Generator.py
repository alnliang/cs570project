def generateString(s, indices):
    for i in indices:
        if i >= 0 and i < len(s)-1:
            s = s[:i+1] + s + s[i+1:]
        else:
            s = s + s
    return s



def main():
    # Read input file
    with open("SampleTestCases/input1.txt", 'r') as f:
        s = ""
        t = ""
        si = []
        ti = []
        for line in f:
            temp = line.strip()
            # Skip empty lines
            if not temp:
                continue
            if temp.isdigit():
                si.append(int(temp))
            else:
                if s != "":
                    t = temp
                    break
                s = temp
        if s == "":
            raise ValueError("Missing first base string in input file")
        
        for line in f:
            temp = line.strip()
            # Skip empty lines instead of raising error
            if not temp:
                continue
            if temp.isdigit():
                ti.append(int(temp))
            else:
                raise ValueError(f"Invalid input")
        # Validate that t was set
        if t == "":
            raise ValueError("Missing second base string in input file")
        
        print(s)
        print(t)
        print(si)
        print(ti)

        print(generateString(s, si))
        print(generateString(t, ti))
        with open("string.txt", 'w') as f:
            f.write(generateString(s, si) + '\n')
            f.write(generateString(t, ti) + '\n')

if __name__ == "__main__":
    main()

