import Tkinter
import tkFileDialog
import tkMessageBox
import random
import math


def getFileName(title):
    root = Tkinter.Tk()
    root.wm_title(title)
    root.withdraw()
    fileName = tkFileDialog.askopenfilename(parent = root)
    while fileName == "":
        fileName = tkFileDialog.askopenfilename(parent = root)
    return fileName

def read(fileName):
    with open(fileName, "r") as file:
        lines = file.readlines()
        lines = lines[1:len(lines) - 1]
        string = ""
        for line in lines:
            string += line
        return "".join(string.split()).decode("base64").encode("hex")

def trim(string):
    size = string[2:4]
    if size == "84":
        return string[12:]
    elif size == "83":
        return string[10:]
    elif size == "82":
        return string[8:]
    elif size == "81":
        return string[6:]
    else:
        return string[4:]

def dissect(seq):
    r = []
    while len(seq) != 0:
        size = seq[2:4]
        if size == "84":
            size = int(seq[4:12], 16) * 2
            temp = seq[12:12 + size]
            seq = seq[12 + size:]
        elif size == "83":
            size = int(seq[4:10], 16) * 2
            temp = seq[10:10 + size]
            seq = seq[10 + size:]
        elif size == "82":
            size = int(seq[4:8], 16) * 2
            temp = seq[8:8 + size]
            seq = seq[8 + size:]
        elif size == "81":
            size = int(seq[4:6], 16) * 2
            temp = seq[6:6 + size]
            seq = seq[6 + size:]
        else:
            size = int(size, 16) * 2
            temp = seq[4:4 + size]
            seq = seq[4 + size:]
        r.append(int(temp, 16))
    return r

def terminate(message):
    tkMessageBox.showerror("ERROR", message)
    quit()

def inform(title, message):
    tkMessageBox.showinfo(title, message)


def main():
    fileName = getFileName("RSA Private Key to Check")
    try:
        string = read(fileName)
        sequence = trim(string)
        v, n, e, d, p, q, dP, dQ, qInv = dissect(sequence)
    except Exception:
        terminate("File / Encoding Error.")
    m = random.getrandbits(int(math.log(n, 2) / 5 * 4))
    c = pow(m, e, n)
    m1 = pow(c, dP, p)
    m2 = pow(c, dQ, q)
    if m1 - m2 >= 0:
        h = qInv * (m1 - m2) % p
    else:
        h = qInv * (m1 + q / p * p - m2) % p
    if pow(c, d, n) == m and m2 + h * q == m:
        with open(fileName + ".txt", "w") as file:
            file.write("n =\n" + str(n) + "\n\n")
            file.write("e =\n" + str(e) + "\n\n")
            file.write("d =\n" + str(d) + "\n\n")
            file.write("p =\n" + str(p) + "\n\n")
            file.write("q =\n" + str(q) + "\n\n")
            file.write("dP =\n" + str(dP) + "\n\n")
            file.write("dQ =\n" + str(dQ) + "\n\n")
            file.write("qInv =\n" + str(qInv))
            inform("Success", "Analysis of " + fileName + " is finished.")
    else:
        terminate("Mathematical Property Check Failed.")


if __name__ == "__main__":
    main()
