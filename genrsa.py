import time
import random
import textwrap
import os


PKCS8_RSA_STRING = "020100300D06092A864886F70D0101010500"


def isProbablePrime(n):
    return pow(random.getrandbits(64), n - 1, n) == 1

def nextProbablePrime(n):
    if n & 1 == 0:
        n += 1
    while not isProbablePrime(n):
        n += 2
    return n

def getPrivateExponent(p, q, e):
    k = 1
    while (k * (p - 1) * (q - 1) + 1) % e != 0:
        k += 1
    return (k * (p - 1) * (q - 1) + 1) / e

def appendSizePrefix(b):
    size = len(b) / 2
    if size <= 0x7F:
        b = format(size, "x") + b
        b = ("0" if len(b) % 2 == 1 else "") + b
    elif size <= 0xFF:
        b = "81" + format(size, "x") + b
    elif size <= 0xFFFF:
        b = format(size, "x") + b
        b = "82" + ("0" if len(b) % 2 == 1 else "") + b
    elif size <= 0xFFFFFF:
        b = format(size, "x") + b
        b = "83" + ("0" if len(b) % 2 == 1 else "") + b
    else:
        b = format(size, "x") + b
        b = "84" + ("0" if len(b) % 2 == 1 else "") + b
    return b

def longToASN1Int(n):
    n = format(n, "x")
    if len(n) % 2 == 1:
        n = "0" + n
    if n[0] not in [str(i) for i in xrange(8)]:
        n = "00" + n
    return "02" + appendSizePrefix(n)

def getPKCS1Sequence(n, e, d, p, q, dP, dQ, qInv):
    v = longToASN1Int(0)
    n = longToASN1Int(n)
    e = longToASN1Int(e)
    d = longToASN1Int(d)
    p = longToASN1Int(p)
    q = longToASN1Int(q)
    dP = longToASN1Int(dP)
    dQ = longToASN1Int(dQ)
    qInv = longToASN1Int(qInv)
    s = v + n + e + d + p + q + dP + dQ + qInv
    return "30" + appendSizePrefix(s)

def getPKCS1Octet(b):
    return "04" + appendSizePrefix(b)

def getSequence(b):
    return "30" + appendSizePrefix(b)

def createKey(size, fileName):
    start = time.time()
    p = random.SystemRandom().getrandbits(size / 2)
    q = (random.SystemRandom().getrandbits(size) | 1 << size - 1) / p
    p = nextProbablePrime(p)
    q = nextProbablePrime(q)
    e = 65537
    d = getPrivateExponent(p, q, e)
    n = p * q
    m = random.getrandbits(64)
    if pow(pow(m, e, n), d, n) == m:
        if p < q:
            p, q = q, p
        dP = d % (p - 1)
        dQ = d % (q - 1)
        qInv = pow(q, p - 2, p)
        seq = getPKCS1Sequence(n, e, d, p, q, dP, dQ, qInv)
        seq = getSequence(PKCS8_RSA_STRING + getPKCS1Octet(seq))
        base64 = "".join(seq.decode("hex").encode("base64").split())
        with open(fileName, "w") as file:
            file.write("-----BEGIN PRIVATE KEY-----\n")
            file.write(textwrap.fill(base64, 64))
            file.write("\n-----END PRIVATE KEY-----\n")
        finish = time.time()
        print "Time Taken: " + str(round(finish - start, 3)) + " Seconds"
    else:
        print "KEY NOT VALID - Regenerating Key"
        createKey(size, fileName)


if __name__ == "__main__":
    size = int(raw_input("Enter RSA Key Size: "))
    amount = int(raw_input("Enter Number of Key Pairs to Create: "))
    for i in xrange(amount):
        print "\n" + str(i + 1) + "."
        createKey(size, "RSA PRIVATE KEY " + str(i + 1) + ".key")
    os.system("pause")
