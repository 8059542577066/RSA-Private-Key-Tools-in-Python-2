import time
import random
import textwrap
import os


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

def longToASN1Int(n):
    n = format(n, "x")
    if len(n) % 2 == 1:
        n = "0" + n
    if n[0] not in [str(i) for i in xrange(8)]:
        n = "00" + n
    size = len(n) / 2
    if size <= 0x7F:
        n = format(size, "x") + n
        n = ("0" if len(n) % 2 == 1 else "") + n
    elif size <= 0xFF:
        n = "81" + format(size, "x") + n
    elif size <= 0xFFFF:
        n = format(size, "x") + n
        n = "82" + ("0" if len(n) % 2 == 1 else "") + n
    elif size <= 0xFFFFFF:
        n = format(size, "x") + n
        n = "83" + ("0" if len(n) % 2 == 1 else "") + n
    else:
        n = format(size, "x") + n
        n = "84" + ("0" if len(n) % 2 == 1 else "") + n
    return "02" + n

def getSequence(n, e, d, p, q, dP, dQ, qInv):
    v = longToASN1Int(0)
    n = longToASN1Int(n)
    e = longToASN1Int(e)
    d = longToASN1Int(d)
    p = longToASN1Int(p)
    q = longToASN1Int(q)
    dP = longToASN1Int(dP)
    dQ = longToASN1Int(dQ)
    qInv = longToASN1Int(qInv)
    r = v + n + e + d + p + q + dP + dQ + qInv
    size = len(r) / 2
    if size <= 0x7F:
        r = format(size, "x") + r
        r = ("0" if len(r) % 2 == 1 else "") + r
    elif size <= 0xFF:
        r = "81" + format(size, "x") + r
    elif size <= 0xFFFF:
        r = format(size, "x") + r
        r = "82" + ("0" if len(r) % 2 == 1 else "") + r
    elif size <= 0xFFFFFF:
        r = format(size, "x") + r
        r = "83" + ("0" if len(r) % 2 == 1 else "") + r
    else:
        r = format(size, "x") + r
        r = "84" + ("0" if len(r) % 2 == 1 else "") + r
    return "30" + r

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
        seq = getSequence(n, e, d, p, q, dP, dQ, qInv)
        base64 = "".join(seq.decode("hex").encode("base64").split())
        with open(fileName, "w") as file:
            file.write("-----BEGIN RSA PRIVATE KEY-----\n")
            file.write(textwrap.fill(base64, 64))
            file.write("\n-----END RSA PRIVATE KEY-----\n")
        finish = time.time()
        print "Time Taken: " + str(round(finish - start, 3)) + " Seconds"
    else:
        print "KEY NOT VALID - Regenerating Key"
        createKey(size, fileName)


size = int(raw_input("Enter RSA Key Size: "))
amount = int(raw_input("Enter Number of Key Pairs to Create: "))
for i in xrange(amount):
    print "\n" + str(i + 1) + "."
    createKey(size, "RSA PRIVATE KEY " + str(i + 1) + ".key")
os.system("pause")
