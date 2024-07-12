from labjack import ljm
import time

import numpy as np
import pandas as pd

from datetime import datetime

########################## READ ME PLEASE ################################
#
#AIN0 AIN1 current measurement (resistor is 0.0492)
#
#AIN2 AIN3 V across sample (using voltage divider;  1/5.4 of the actual voltage is measured)
#
#AIN9 voltage monitoring of BK 9116 0->150V gives 0->5V
#
#AIN10 current monitoring of BK 9116 0->30A gives 0->5A
#
#AIN11 power status on/off
#
#AIN12 AIN13 pool temperature ktype
#
#FIO0 engage power supply; FIO0 = 0 is emergency shut off
#
#DAC0 voltage control input 0->5V gives 0->150V
#
#DAC1 current control input 0->5V gives 0->30A
#
#how to config LABJACK extended features:
#https://labjack.com/support/datasheets/t-series/ain/extended-features
#
#
# Linear Control:
a = 0.0358025	
b = 0.001305129
Ro = 8.239
pooltemp = 90.68 # experiment should end at 150C for manifold

# THE OLD POOL TEMPS WERE MEASURED TO BE 82.52! WHICH IS VERY WRONG

#
######################################################################



###################### FILE INITIALIZATION ######################

filename = "TCRTesting_Heater_10_ "+str(datetime.now())[:-7] 		# MAKE SURE TO CHANGE THE FILENAME EVERY TIME YOU RUN THE EXPIREMENT, also don't write .txt

print('\n date and time:')
print(str(datetime.now())[:-7])

data = open(filename + '.txt', "w") # place to write all the data
#headers:  time,Vsample,Vpowerresistor,Rsample,temperature,power,current,targetvoltage,targetpower,Voltagesupply/3,dv,pooltemp,	integral,powerj,currentj,ljmcurrent,\n

data.writelines('time,Vsample,Vpowerresistor,Rsample,temperature,power,current,targetvoltage,targetpower,Voltagesupply,dv,pooltemp,integral,powerj,currentj,ljmcurrent,Ro\n') # Header line in the txt file

################# Configuring Labjack Extended Features ################# 

handle = ljm.openS("ANY", "ANY", "ANY")    # Open first found LabJack

#how to config LABJACK
#https://labjack.com/support/datasheets/t-series/ain/extended-features

ljm.eWriteName(handle,'AIN0_NEGATIVE_CH',1) # the value is the negative channel chosen (always AIN# +1)
ljm.eWriteName(handle,'AIN0_RANGE',0)

ljm.eWriteName(handle,'AIN2_NEGATIVE_CH',3) # the value is the negative channel chosen (always AIN# +1)
ljm.eWriteName(handle,'AIN2_RANGE',0) # 


# pooltemp = (RTD-1289.87)/(1385.06-1289.87)*(100-75) + 75 #HARDCODED NOW 
# pooltemp = ljm.eReadName(handle,'AIN12_EF_READ_A') -273.15 -2 # how to read from ktype EF 

print('pool temperature:  ',pooltemp)
print('this is a hardcoded value for pool temp, make sure to update this')
time.sleep(2)

################### Preparing Fail Safe  ###################
ljm.eWriteName(handle,'DAC0',0) 
ljm.eWriteName(handle,'DAC1',0) 
ljm.eWriteName(handle,'FIO0',0)
ljm.eWriteName(handle,'FIO0',1)


################### Finding Initial Resistance ###################

ljm.eWriteName(handle,'DAC0',53/30)   # input * 30 as the max voltage
ljm.eWriteName(handle,'DAC1',0.15/6) # current control: should give single watt of power 
time.sleep(2) # let it come to temp to read the initial resistance value

# getting an accurate reading for initial resistance
									
test = np.zeros(100)
i_test = 0
Rpowerresistor = 0.0504	 # Ohms

while i_test < 100:
	Vsample = (ljm.eReadName(handle,'AIN2'))*(0.995+10.04)/0.995
	Vpowerresistor = abs(ljm.eReadName(handle,'AIN0') )
	current =  Vpowerresistor/ Rpowerresistor
	Rsample = Vsample/current
	test[i_test] = Rsample
	i_test += 1

power = Vsample*current

Vsample = (ljm.eReadName(handle,'AIN2'))*(0.995+10.04)/0.995 # voltage divider

Vpowerresistor = abs(ljm.eReadName(handle,'AIN0') )
current =  Vpowerresistor/ Rpowerresistor 			## Finding Current

#current_test = ljm.eReadName(handle,'AIN10')*6 # not worth using

power = Vsample*current
Rsample = np.average(test)  

print('\n Testing Power Supply:')
print(power,'W power')
print(Rsample)
time.sleep(1)

#################### Preparing Cutoff Values ####################


TCR = 0.001568	# FIX THIS				
#######################################################UPDATE THIS
tempinitial = pooltemp 					# starting temperature
temperatureburning = 150				# cutoff temperature, 140 is safe, bring it close to the critical superheat
Rinitial = Rsample							# Using inital resistance
Rburning = Ro*(1+(TCR*(temperatureburning-tempinitial))) # Solving the cutoff resistance using TCR equation
voltagecutoff  = 53  													# just to make sure the control doesn't go haywire

print('\n Initial Values: ')
print('R_initial: ','{:2.2f}'.format(Rinitial),'R_burning: ', '{:2.2f}'.format(Rburning),'\n')
j = 1
integral = 0
Po = 1
TESTCUTOFF = 0
time.sleep(1)

###################### Start experiment ###################### 

Run = True
if Vsample < 0:
	run = False 
	print('Vsample leads are in the negative config \n please fix before continuing \n \n \n')


targetpower = Po
Voltagesupply = 0.3
t0 = time.time()							# start to record time in seconds 
t = 0
targetvoltage = 0
dV = 0
ljm.eWriteName(handle,'DAC0',53/30)   # input * 30 as the max voltage
time.sleep(1)
while  Run == True:

	### Finding Target Power ###
	powerfile = open("TargetPower")					# finding the target power from TargetPower (a file that is created by the controller 
	targetpowerold = targetpower						# fixing the '' error
	targetpower = powerfile.readline() 					# collecting targetpower value
	if targetpower == '':									# fixing the error in which targetpower == ''
		targetpower = targetpowerold

	### Finding System Current ###
	Vpowerresistor = abs(ljm.eReadName(handle,'AIN0'))		# Collecting voltage across the power resistor 
	current =  Vpowerresistor/ Rpowerresistor 			# Finding Current from the power resistor

	### Finding Sample Voltage and Resistance ###
	Vsample = abs(ljm.eReadName(handle,'AIN2') ) * (0.995+10.04)/0.995 # Sample voltage; the 5.4 referse to the voltage divider for collecting voltage
	Rsample = Vsample/current								# resistance from Ohms Law
	power = Vsample*current			# Calculating Power as (Across the sample) * Current

	### Temperatures ###
	#pooltemp = ljm.eReadName(handle,'AIN12_EF_READ_A') -273.15 -2
	temperature = (Rsample/Ro - 1)/TCR + tempinitial  		# using the equation for temperature coefficient of resistance

	### Roman's control for current defined system ###

	integral += (1/a)*b*np.exp(-a*j)*float(targetpower)
	powerj = Po*np.exp(-(a)*j) + integral
	currentj = (powerj/Ro)**0.5 -0.1  # currentj and powerj represent the moving target approaching targetpower at moment j (j being the itteration), 10.7 is the estimated resistance of the heater
	ljmcurrent = currentj/6 # ljm goes 0 to 5, which corresponds to 0-30 amps on the supply
	
	j += 1
	if targetpower != targetpowerold: # when target power changes, reset algorithm 
		integral = 0
		j =1
		Po = float(targetpowerold)
	ljm.eWriteName(handle,'DAC1',ljmcurrent)

	### display live data of temp, Rsample, Power, Current, Vsample ###
	print( '{:1.6f}'.format(Rsample),'Ohms ','{:3.2f}'.format(power),'W','{:2.3f}'.format(current),'A','{:2.3f}'.format(Vsample),'Volts ','{:3.1f}'.format(temperature),'C Temp' )

	### Writing File Data ###
	t = time.time() - t0   					# timer :^)

	# t, Vsample, Vpowerresistor,Rsample,temperature,power,current,targetvoltage,targetpower,Voltagesupply/3,dv,pooltemp,	integral,powerj,currentj,ljmcurrent
	data.writelines([str(t),',', str(Vsample),',',str(Vpowerresistor),',', str(Rsample) ,',', str(temperature),',',str(power),',',str(current),',',str(targetvoltage),',',str(targetpower),',',str(Voltagesupply),',',str(dV),',',str(pooltemp),',',str(integral),',',str(powerj),',',str(currentj),',',str(ljmcurrent),',',str(Ro),'\n'])
	
	### System Failsafe ###
	if Rsample > Rburning or Voltagesupply > voltagecutoff or float(targetpower) == 0.123123: # cutoff check
		TESTCUTOFF = TESTCUTOFF +1
		print('step one of fail safe triggered')
	else:
		TESTCUTOFF = 0
		

	if TESTCUTOFF > 2:
		print('fail safe reached')
		ljm.eWriteName(handle,'FIO0',0)
		ljm.eWriteName(handle,'DAC0',0)
		ljm.eWriteName(handle,'DAC1',0)
		data.close()
		Run = False
	
	
ljm.eWriteName(handle,'FIO0',0) # shut off power supply
ljm.eWriteName(handle,'DAC0',0)
ljm.eWriteName(handle,'DAC1',0)



