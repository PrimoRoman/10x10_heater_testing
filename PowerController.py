import numpy as np
import matplotlib.pyplot as plt
import time



## CHF TEST ## Manifold
TargetFile = open('TargetPower', "w").writelines('1') # place to write all the data
print('1')
time.sleep(10)

PowerSteps = np.linspace(2,150,15) # declaring the set target powers
for i in range(len(PowerSteps)):
    print(PowerSteps[i])
    TargetFile = open('TargetPower', "w").writelines(str(PowerSteps[i])) # place to write all the data
    time.sleep(45)

time.sleep(15)

PowerSteps = np.linspace(155,300,40) # multiiisteeeeeeep
for i in range(len(PowerSteps)):
    print(PowerSteps[i])
    TargetFile = open('TargetPower', "w").writelines(str(PowerSteps[i])) # place to write all the data
    time.sleep(60)




### HEAT LOSS TEST ##
#TargetFile = open('TargetPower', "w").writelines('1') # place to write all the data
#print('1')
#time.sleep(15)
#PowerSteps = np.linspace(1,5,5) # declaring the set target powers
#for i in range(len(PowerSteps)):
#    print(PowerSteps[i])
#    TargetFile = open('TargetPower', "w").writelines(str(PowerSteps[i])) # place to write all the data
#    time.sleep(600)





### CHF TEST ## no manifold ##
#TargetFile = open('TargetPower', "w").writelines('1') # place to write all the data
#print('1')
#time.sleep(15)
#PowerSteps = np.linspace(2,27,7) # declaring the set target powers
#for i in range(len(PowerSteps)):
#    print(PowerSteps[i])
#    TargetFile = open('TargetPower', "w").writelines(str(PowerSteps[i])) # place to write all the data
#    time.sleep(60)

#PowerSteps = np.linspace(30,80,30) # multiiisteeeeeeep
#for i in range(len(PowerSteps)):
#    print(PowerSteps[i])
#    TargetFile = open('TargetPower', "w").writelines(str(PowerSteps[i])) # place to write all the data
#    time.sleep(60)


## END EXPERIMENT
TargetFile = open('TargetPower', "w").writelines('1') # Reset to 1 
time.sleep(3)
TargetFile = open('TargetPower', "w").writelines('0.123123') # ends experiment
time.sleep(1)
print('end')
