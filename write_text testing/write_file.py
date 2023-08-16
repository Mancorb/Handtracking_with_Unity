from random import randint
files=["A","B","C","D"]
counter =0
loops = 0

for i in range(35):
    for name in files:
        location = f"./Hand_{name}/[{counter}].txt" #Hand_A/[0]
        
        with open(location,"w") as file:
            for point in range(21):
                file.write(str(randint(0,255))+","+str(randint(0,255))+","+str(randint(0,255))+"\n")
            file.write(str(randint(220,600)))
    counter +=1
    if counter == 20:
        counter =0

print("\nProcess done...")