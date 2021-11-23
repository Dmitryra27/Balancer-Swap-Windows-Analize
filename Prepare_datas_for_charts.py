#!/usr/bin/env python
# coding: utf-8

# In[7]:


from Balancer_lib import *
from Datas_4 import *
import plotly
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import random
import numpy as np
import pandas as pd
print('Start prices AAVE, SUSHI, YFU, SNX',datas[0])


# In[8]:


def swap_1step_weights(pool, weights, datas, fee, n, weigths1, index ):#We have pool, weights and get new weigths1
    val0=value(pool, datas, index, n)#стоимость пула в момент = index
    data_for_swap1 = calc_arbitr_one_dir1(pool, weights, datas, index, n, 0, 0, val0, fee)
    pool1=one_swap(pool, data_for_swap1, fee, n)
    for i in range(0,10,1):
        data_for_swap1 = calc_arbitr_one_dir1(pool1, weights, datas, index, n, 0, 0, val0, fee)
        
        pool1=one_swap(pool1, data_for_swap1, fee, n)
    
    return [pool1, weights1]


# In[9]:


#Collect datas for Charts - 
#Strategy 1 - change ratio to new ratio1 and SWAP for 1 period in moment=index 
# We computer losses of pool and other parametrs accoding the moment=index of applying new ratio1 and open Swap Window
#In this Model We may change this parametrs only
capital = 4000000 # TVL in USD 
start_index=1
step=3
fee=0.003
steps_max=3000
ratio1 = [0.45, 0.25, 0.25, 0.05]# DAO decides to change ratio to ratio1
#----other params----
n=4
amount_step=0.01 
accuracy=0
proc=0.01
#---------------------
weights=[0.25]*n
pool = [0]*n

for i in range(0,n):
    pool[i]=round(capital/datas[start_index][i]/4, 1)
pool0=pool
x=[]
loss1=[]# Losses
val0=[]
val1=[]#Values of Pools with diffrent strtegies
#Cost of Token in pool with diffrenet strategies
st10=[]# Strategy, Cost of Token in Pool,
st11=[]
st12=[]
st13=[]

stpr10=[]# Strategy, Cost of Token in Pool,
stpr11=[]
stpr12=[]
stpr13=[]

pr0=[]#prices of Tokens
pr1=[]
pr2=[]
pr3=[]
dpr1=[]
dpr2=[]
w10=[]#weights for 1 strategy
w11=[]
w12=[]
w13=[]

count=0

for index in range(start_index,len(datas)-1-step, step):
    x.append(count)
    val00=value(pool, datas, index, n)
    v0=value(pool0, datas, index, n)
    #print('v0=', v0)
    val0.append(v0)
    pr0.append(datas[index][0])
    pr1.append(datas[index][1])
    pr2.append(datas[index][2])
    pr3.append(datas[index][3])
    dpr1.append((datas[index+step][1]-datas[index+step][1])/datas[index][1]*100)
    dpr2.append((datas[index+step][2]-datas[index+step][2])/datas[index][2]*100)
    #------------
    res1=swap_1step_ratio(pool, weights, datas, fee, n, ratio1, index )
    p1=res1[0]
    w1=res1[1]
    st10.append(p1[0]*datas[index][0])
    st11.append(p1[1]*datas[index][1])
    st12.append(p1[2]*datas[index][2])
    st13.append(p1[3]*datas[index][3])
    st1=p1[0]*datas[index][0]+p1[1]*datas[index][1]+p1[2]*datas[index][2]+p1[3]*datas[index][3]
    stpr10.append(p1[0]*datas[index][0]/st1)
    stpr11.append(p1[1]*datas[index][1]/st1)
    stpr12.append(p1[2]*datas[index][2]/st1)
    stpr13.append(p1[3]*datas[index][3]/st1)
    
    w10.append(w1[0])
    w11.append(w1[1])
    w12.append(w1[2])
    w13.append(w1[3])
    
    val11=value(p1, datas, index, n)
    val1.append(val11)
    loss1.append(-val11+val00)
    count=count+1
    #---------


# In[10]:


#Collect datas for Charts - 
#Strategy 2 - we decide change ratio to new ratio1
# We plan to open SWAP Window and allow to Arbitrages to make swaps by  100 steps starting from moment=start_index and stop at index=2179 (end of datas)
# We computer losses of pool and other parametrs accoding the start moment=index of applying new ratio1
weights=[0.25]*n
weights1=[0.25]*n
pool = [0]*n
delta_weights=[0]*n
count_step_max=0
step=3
fee=0.003
steps_max=3000

for i in range(0,n):
    pool[i]=round(capital/datas[start_index][i]/4, 1)
#-------------
loss2=[]# Losses
#Values of Pools with diffrent strategies
val2=[]

st20=[]
st21=[]
st22=[]
st23=[]

stpr20=[]
stpr21=[]
stpr22=[]
stpr23=[]

w20=[]
w21=[]
w22=[]
w23=[]
#----------------
val00=value(pool, datas, index, n)#стоимость пула в момент = index
pool_new = pool_from_ratio_value(ratio1, datas, index, val00, n) 
weights_end= calc_weights(pool_new, weights, datas, start_index, n, amount_step, accuracy, val00)
#print('weights_end= ', weights_end )
index_end=len(datas)

    
if steps_max>int((index_end - start_index)/step):
    steps_max = int((index_end - start_index)/step)
for i in range(0,n,1):
        delta_weights[i]=weights_end[i]-weights[i]
#print('delta_weights ',  delta_weights)
for index in range(start_index,len(datas)-1-step, step):
    #apply next weights with small step each SWAP Window 
    if (count_step_max<steps_max):
        count_step_max = count_step_max+1
        for i in range(0,n,1):
            weights1[i]=weights1[i]+delta_weights[i]/steps_max
        #print('weights1= ', weights1)
        res2=swap_1step_weights(pool, weights, datas, fee, n, weights1, index )
        
        p2=res2[0]
        w2=res2[1]
        
    st20.append(p2[0]*datas[index][0])
    st21.append(p2[1]*datas[index][1])
    st22.append(p2[2]*datas[index][2])
    st23.append(p2[3]*datas[index][3])
    st2=p2[0]*datas[index][0]+p2[1]*datas[index][1]+p2[2]*datas[index][2]+p2[3]*datas[index][3]
    stpr20.append(p2[0]*datas[index][0]/st2)
    stpr21.append(p2[1]*datas[index][1]/st2)
    stpr22.append(p2[2]*datas[index][2]/st2)
    stpr23.append(p2[3]*datas[index][3]/st2)
    w20.append(w2[0])
    w21.append(w2[1])
    w22.append(w2[2])
    w23.append(w2[3])
    
    val21=value(p2, datas, index, n)
    val2.append(val21)
    loss2.append(val21-val00)
    weights=weights1
    #-----------


# In[11]:


#Collect datas for Charts - 
#Strategy 3 - we decide change ratio to new ratio1
# We plan to open SWAP Window and allow to Arbitrages to make swaps by  50 steps  or smaller starting from moment=start_index and stop at index=2179 (end of datas)
# We computer losses of pool and other parametrs accoding the start moment=index of applying new ratio1
weights=[0.25]*n
weights1=[0.25]*n
pool = [0]*n
delta_weights=[0]*n
start_index=0
steps_max=30
count_step_max=0
proc=0.01
ratio1=[0.45,0.25,0.25,0.05]
for i in range(0,n):
    pool[i]=round(capital/datas[start_index][i]/4, 1)
#-------------
loss3=[]
val3=[]

st30=[]
st31=[]
st32=[]
st33=[]

stpr30=[]
stpr31=[]
stpr32=[]
stpr33=[]

w30=[]
w31=[]#weights for 3 strategy
w32=[]
w33=[]
#------------
val0_0=value(pool, datas, index, n)#стоимость пула в момент = index
pool_new = pool_from_ratio_value(ratio1, datas, index, val0_0, n) 
weights_end= calc_weights(pool_new, weights, datas, start_index, n, amount_step, accuracy, val0_0) 
#print('weights_end= ', weights_end )
index_end=len(datas)
#-----------
steps_max1=int((index_end - start_index)/step)
steps_max = min(steps_max, steps_max1)
#print('steps_max= ', steps_max )
for i in range(0,n,1):
        delta_weights[i]=weights_end[i]-weights[i]

for index in range(start_index,len(datas)-1-step, step):
    
    #apply next weights with small step each SWAP Window when the price movement> pros
    if index==start_index:
        for i in range(0,n,1):
            weights1[i]=weights1[i]+delta_weights[i]/steps_max
        res3=swap_1step_weights(pool, weights, datas, fee, n, weights1, index )
        p3=res3[0]
        w3=res3[1]
    #print('we, we1=', weights,weights1)
    #print(((datas[index+step][1]-datas[index][1])/datas[index][1]))
    if (count_step_max<steps_max) and (((datas[index+step][0]-datas[index][0])/datas[index][0])>proc and ((datas[index+step][3]-datas[index][3])/datas[index][3])<proc):
        #print('Price movement is good')
        for i in range(0,n,1):
            weights1[i]=weights1[i]+delta_weights[i]/steps_max
        #print('weights1 = ', weights1)
        count_step_max=count_step_max+1
        res3=swap_1step_weights(pool, weights, datas, fee, n, weights1, index )
        p3=res3[0]
        w3=res3[1]
        #print('w3= ', w3)
        
    w30.append(w3[0])
    w31.append(w3[1])
    w32.append(w3[2])
    w33.append(w3[3])
    st30.append(p3[0]*datas[index][0])
    st31.append(p3[1]*datas[index][1])
    st32.append(p3[2]*datas[index][2])
    st31.append(p3[3]*datas[index][3])
    st3=p3[0]*datas[index][0]+p3[1]*datas[index][1]+p3[2]*datas[index][2]+p3[3]*datas[index][3]
    #print('st3= ', st3)
    stpr30.append(p3[0]*datas[index][0]/st3)
    stpr31.append(p3[1]*datas[index][1]/st3)
    stpr32.append(p3[2]*datas[index][2]/st3)
    stpr33.append(p3[3]*datas[index][3]/st3)
    
    val31=value(p3, datas, index, n)
    val3.append(val31)
    loss3.append(val31-val0_0)
    
        
    weights=weights1


# In[ ]:




