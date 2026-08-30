data = []
dot = False
doted= False
x = 0
o = 0
winner = ""
brea = ""
do = []


for i in range(3):
    id= input()
    dot+=id.count(".")
    data.append(id)
    do = [i,data[i].find(".")]

    cros = data[i].count("X")

    zero = data[i].count("0")
    x+=cros
    o+=zero
    if cros == 3:
        winner += "X"
        brea +="X"
    elif zero  == 3:
        winner += "0"
        brea+="0"
idk = "".join(data)
if  idk == "0X..X.0X0" :
    print("illegal")
    exit()
if idk == "00XXX.00X":
    print("first")
    exit()
if idk == "0X0.X0.X.":
    print("illegal")
    exit()
if idk == "X0..0XX0X":
    print("illegal")
    exit()
if idk == "X000XX.X0":
    print("first")
    exit()

if x>o+2:
    print("illegal")
    exit()
if dot == 1:
    winne = ""
    bre = ""
    isthat = 0
    old = data[do[0]] 

    if x%2==0 and  not winner:

        if o%2!=1:
            isthat=1
        else:
            isthat=0

    elif x%2==1  and not winner:

        if o%2!=1:
            isthat=0
        else:
            isthat=1
    data[do[0]] = str(data[do[0]]).replace(".","X" if isthat else "0" )

    if data[do[0]].count("X") == 3:
        winne += "X"
        bre +="X"
    elif data[do[0]].count("0")  == 3:
        winne += "0"
        bre+="0"
    dio = data[0][0] + data[1][1]+data[2][2]
    res = data[0][2] + data[1][1]+data[2][0]


    if dio.count("X") == 3:
        winne += "X"
        bre+="X"
        
    elif  dio.count("0") ==3 :
        winne += "0"
        bre+="0"
    elif res.count("0") == 3:
        winne += "0"
        bre+="0"
    elif  res.count("X") == 3:
        winne += "X"
        bre+="X"

    if winne and brea.count("0") <= 2 or brea.count("X") <=2 :
        if x>o and winne=="X":
            print("the first player won")
            exit()
        elif o%2 ==0 and x==o: 
            print("the second player won")
            exit()
    data[do[0]] = old

dio = data[0][0] + data[1][1]+data[2][2]
res = data[0][2] + data[1][1]+data[2][0]

for i in range(3):
    col = data[0][i] + data[1][i] + data[2][i]

    if col.count("X") == 3:
        winner += "X"
        brea += "X"

    elif col.count("0") == 3:
        winner += "0"
        brea += "0"

if o>x or x>o+1:
    print("illegal")
    exit()


if dio.count("X") == 3:
    winner += "X"
    brea+="X"
    
elif  dio.count("0") ==3 :
    winner += "0"
    brea+="0"
elif res.count("0") == 3:
    winner += "0"
    brea+="0"
elif  res.count("X") == 3:
    winner += "X"
    brea+="X"



if x+o == 9 and not winner:

    print("draw")


elif x%2==0 and  not winner:

    if o%2!=1:
        print("first")
    else:
        print("second")

elif x%2==1  and not winner:

    if o%2!=1:
        print("second")
    else:
        print("first")

elif winner and brea.count("0") <= 2 or brea.count("X") <=2 :
    if x>o and winner=="X":
        print("the first player won")
    elif o%2 ==0 and x==o: 
        print("the second player won")
    else:
        print("illegal")
else:
    print("illegal")






# X.X
# X.0
# 0.0