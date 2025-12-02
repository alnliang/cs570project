def generateString(s, indices):
    for i in indices:
        if i >= 0 and i < len(s)-1:
            s = s[:i+1] + s + s[i+1:]
        else:
            s = s + s
    return s



import argparse


def main():
    parser = argparse.ArgumentParser(description="Generate expanded strings from input file")
    parser.add_argument('input_file', help='Path to the input file listing base strings and indices')
    args = parser.parse_args()

    # Read input file
    with open(args.input_file, 'r') as f:
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
        
        # Output only the generated strings to stdout for downstream scripts
        gen_s = generateString(s, si)
        gen_t = generateString(t, ti)
        print(gen_s)
        print(gen_t)
        # Also write to string.txt for local debugging compatibility
        with open("string.txt", 'w') as sf:
            sf.write(gen_s + '\n')
            sf.write(gen_t + '\n')

if __name__ == "__main__":
    main()

