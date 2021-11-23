#!/usr/bin/env python
# coding: utf-8

# In[8]:


# define functions for prices

def constanta (pool, weights, n):
    k=1
    for i in range(0,n,1):
        k=k*(pool[i]**weights[i])
    return k

#----------------
# value of pool
def value(pool, datas, step, n):
    v=0
    for i in range(0,n,1):
        v=v+pool[i]*datas[step][i]
        #print(v)
    return v

#-----------------
def pool_for_spot_usd(pool, value0, n):
    pool_1 =[0]*n
    for i in range(0,n,1):
        pool_1[i]=pool[i]
    pool_1.append(value0/n)
    return pool_1

#-----------------
#calc price in USD in moment = step
def market_price_usd(datas, step, n):
    pr=[0]*n
    for i in range(0,n,1):
        pr[i]=datas[step][i]
    return pr
#------------------

def spot_price_usd(pool, weights, datas, step, n, value0):
    pr=[0]*n
    usd_cost=pool_for_spot_usd(pool, value0, n)[n]
    for i in range(0,n,1):
        pr[i]=usd_cost*weights[i]/pool[i]/(1/n)
            
    return pr

#-------------------
#Computer the price difference between spot and market prices
def delta_spot_market_usd(pool, weights, datas, step, n, value0):
    d=[0]*n
    sp=spot_price_usd(pool, weights, datas, step, n, value0)
    #print('sp = ', sp)
    mp=market_price_usd(datas, step, n)
    #print('mp = ', mp)
    for i in range(0,n,1):
        d[i]=sp[i]-mp[i]
    return d


# In[2]:


#Functiouns for calculation swaps
def calc_out_given_in(pool, weights, fee, amount_in, dir_in, dir_out, n):# dir_in, amount_in, dir_out, amount_out 
    
    k=constanta (pool, weights, n) 
    totalfee=[0]*n
    a1=5
    a2=5
    for i in range(0,n,1):
        if (i!=int(dir_in)) and (i!=int(dir_out)):
            if a1!=5 and a2==5:
                a2=i
            if a1==5:
                a1=i
    amount_out=pool[dir_out] - (k/((pool[dir_in]+amount_in*(1-fee))**weights[dir_in])/(pool[a1]**weights[a1])/(pool[a2]**weights[a2]))**(1/weights[dir_out])
    return [  dir_in, amount_in, dir_out, amount_out ]# dir_in, amount_in, dir_out, amount_out 
#------------------------------
def calc_in_given_out(pool, weights, fee, amount_out, dir_in, dir_out, n):
    
    k=constanta (pool, weights, n) 
    print('k', k)
    totalfee=[0]*n
    a1=5
    a2=5
    for i in range(0,n,1):
        if (i!=int(dir_in)) and (i!=int(dir_out)):
            if a1!=5 and a2==5:
                a2=i
            if a1==5:
                a1=i
    print( dir_in, dir_out, a1, a2)
    amount_in= abs((- pool[dir_in] + (k/((pool[dir_out]+amount_out)**weights[dir_out])/(pool[a1]**weights[a1])/(pool[a2]**weights[a2]))**(1/weights[dir_in]))/(1-fee))
    #amount_in = 
    
    return [dir_in, amount_in, dir_out, amount_out ]#out, dir_out,amount_in, dir_in


# In[3]:


# functions for calculate new pools from new ratio
#calc new pool from given new ratio and value of old pool

def pool_from_ratio_value(ratio, datas, step, value, n):# ratio = [], datas, step,total value of pool,
    #print('ratio = ',ratio)
    #print('datas= ',datas)
    #print('value0= ', value0)
    arr=[0]*n
    for i in range(0,n,1):
        arr[i]=value*ratio[i]/datas[step][i]
    return arr

#----------------------
#calc new pool from old pool and new ratio
def pool_from_ratio_oldpool(pool, ratio, datas, step,  n):
    val= value(pool, datas, step, n)
    arr=pool_from_ratio_value(ratio, datas, step, val, n)
    return arr


# In[4]:


# functions for calc new weigths1
#-------------------------
def calc_price_directions(pool, weights, datas, step, n, value0):
    d=delta_spot_market_usd(pool, weights, datas, step, n, value0)
    #print('delta price in calc price direction=', d )
    arr=d
    arr=sorted(arr, reverse = True)
    
    pos=[-1]*n
    for i in range (0,n,1):
        for j in range (0,n,1):
            if arr[i] == d[j]:
                pos[i]=j
    return [arr,pos]

#print('calc_price_directions=',calc_price_directions(pool, weights, datas, step, n, value0))# for check
#-------------
def calc_weights(pool, weights, datas, step, n, weight_step, accuracy, value0):
    
    we=[0]*n
    for i in range(0,len(weights),1):
        we[i]=weights[i]
    #print('we= ', we)
    dir = calc_price_directions(pool, weights, datas, step, n, value0)
    #print('dir in calc_weights on start= ', dir)
    count=0
    while (dir[0][0]/datas[step][dir[1][0]] > accuracy) and (dir[0][n-1]/datas[step][dir[1][n-1]]<(-accuracy) and count<1000 ): 
        #print('count=', count)
        we[dir[1][0]]=we[dir[1][0]]-weight_step
        we[dir[1][n-1]]=we[dir[1][n-1]]+weight_step
        dir = calc_price_directions(pool, we, datas, step, n, value0)
        #print('dir in calc weights', dir)
        count=count+1
    return we


# In[5]:


# functions for computer swap directions and amount_in, amount_out
def calc_amount_one_dir(pool, weights, datas, step, n, amount_step, accuracy, value0, fee):
    amount_in=0
    amount_out=[0]*4
    pool11=[0]*n
    for i in range(0,len(pool),1):
        pool11[i]=pool[i]
    #print('pool on start in calc_amount= ', pool11)
    dir = calc_price_directions(pool, weights, datas, step, n, value0)
    print('dir for plan swap in calc_amount', dir)
    dir_in = dir[1][0]
    dir_out = dir[1][n-1]
    #print('dir_in, dir_out in calc_amount_one= ', dir_in, dir_out)
    count=0
    if (dir[0][0]/datas[step][dir[1][0]] > accuracy) and (dir[0][n-1]/datas[step][dir[1][n-1]]<(-accuracy)):
        while (dir[0][0]/datas[step][dir[1][0]] > accuracy) and (dir[0][n-1]/datas[step][dir[1][n-1]]<(-accuracy) and count<1000 and dir_out==dir[1][n-1] and dir_in==dir[1][0]  ): 
            amount_in=amount_in+amount_step
            amount_out = calc_out_given_in(pool11, weights, fee, amount_in, dir_in, dir_out, n)
            pool11[dir[1][0]]=pool[dir[1][0]]+amount_in
            pool11[dir[1][n-1]]=pool[dir[1][n-1]]-amount_out[3]
            #print(count, ' pool = ', pool11)
            dir = calc_price_directions(pool11, weights, datas, step, n, value0)
            #print('dir in calc_am_one_dir= ', dir)
            count=count+1
    else:
        dir_in=0
        dir_out=0
        amount_out[3]=0
    return  [dir_in, amount_in, dir_out, amount_out[3]]#[dir_in, amount_in, dir_out, amount_out]
#-------------
def one_swap(pool, datas_for_swap, fee, n):#datas_for_swap = [dir_in, amount_in, dir_out, amount_out]
    pool_res=[0]*n
    for i in range (0,n,1):
        pool_res[i]=pool[i]
    swap_fee=[0,0,0,0]
    #print( 'datas_for_swap= ',datas_for_swap)
    if datas_for_swap[1]>0 and datas_for_swap[3]>0:
        pool_res[datas_for_swap[0]]=pool_res[datas_for_swap[0]]+datas_for_swap[1]
        pool_res[datas_for_swap[2]]=pool_res[datas_for_swap[2]]-datas_for_swap[3]
    
    return pool_res
#------------------
def swaps(pool, weights, datas, step, n, amount_step, accuracy, value0, fee,k):
    pool_2=[0]*n
    for i in range (0,n,1):
        pool_2[i]=pool[i]
    
    for i in range(0,k,1):
        sw1 = calc_amount_one_dir(pool_2, weights, datas, step, n, amount_step, accuracy, value0, fee)
        pool_2= one_swap(pool1, sw1, fee, n)
        #print('pool_2_in process= ',pool_2)
        print('------------')
    return pool_2


# In[7]:


def arbitr_profit(pool,pool3,datas,step, n):#old pool, new pool
    profit = 0
    for i in range(0,n,1):
        profit = profit- (pool3[i]-pool[i])*datas[step][i]
    return profit

#---------------------
def arbitr_swap(pool, weights1, datas, step1, n, amount_step, accuracy, value0, fee):
    pool4=[]
    sw1 = calc_amount_one_dir(pool, weights1, datas, step1, n, amount_step, accuracy, value0, fee)
    print('sw1= ', sw1)
    pool3= one_swap(pool, sw1, fee, n)
    if arbitr_profit(pool,pool3,datas,step, n)>0:
        print('arbitr profit')
        return pool4
    else:
        print('SWAP is not profitable for arbitrager ! Swap have not made!')
        print('Pool is the same!')
        print('pool= ', pool)
        return pool
#--------------------------


# In[ ]:


def get_ratio(pool, datas, step, n):
    r=[0]*n
    r1=[0]*n
    s=0
    for i in range(0,n,1):
        r[i]=pool[i]*datas[step][i]
        s=s+r[i]
    for i in range(0,n,1):
        r1[i]=r[i]/s
    
    return r1


# In[ ]:


def calc_arbitr_one_dir(pool, weights, datas, step, n, amount_step, accuracy, value0, fee):
    amount_in=0
    amount_out=[0]*4
    pool11=[0]*n
    for i in range(0,len(pool),1):
        pool11[i]=pool[i]
    #print('pool on start in calc_amount= ', pool11)
    dir = calc_price_directions(pool, weights, datas, step, n, value0)
    #print('dir for plan swap in calc_amount', dir)
    dir_in = dir[1][0]
    dir_out = dir[1][n-1]
    #print('dir_in, dir_out in calc_amount_one= ', dir_in, dir_out)
    profit_max=0
    count=0
    if (dir[0][0]/datas[step][dir[1][0]] > accuracy) and (dir[0][n-1]/datas[step][dir[1][n-1]]<(-accuracy)):
        while (dir[0][0]/datas[step][dir[1][0]] > accuracy) and (dir[0][n-1]/datas[step][dir[1][n-1]]<(-accuracy) and count<200 and dir_out==dir[1][n-1] and dir_in==dir[1][0]  ): 
            amount_in=amount_in+amount_step
            amount_out = calc_out_given_in(pool11, weights, fee, amount_in, dir_in, dir_out, n)
            #print('in/out', amount_in,' ', amount_out[3])
            pr = amount_out[3]*datas[step][dir[1][n-1]] - amount_in*datas[step][dir[1][0]]
            #print('pr=', pr)
            if profit_max<pr:
                pool11[dir[1][0]]=pool[dir[1][0]]+amount_in
                pool11[dir[1][n-1]]=pool[dir[1][n-1]]-amount_out[3]
                profit_max=pr
                #print(count, ' pool = ', pool11)
            dir = calc_price_directions(pool11, weights, datas, step, n, value0)
            #print('dir in calc_am_one_dir= ', dir)
            count=count+1
            #print('count= ', count)
    else:
        dir_in=0
        dir_out=0
        amount_out[3]=0
    return  [dir_in, amount_in, dir_out, amount_out[3]]#[dir_in, amount_in, dir_out, amount_out]


# In[ ]:


import random
def random_ratio(n, start, stop, d ):
    w=[0]*n
    w[0]=round(random.uniform(start, stop), 3)
    w[1]=round(random.uniform(start, stop),3)
    rest = 1-w[0]-w[1]
    w[2]=round(random.uniform(rest/2-d, rest/2+d), 3)
    w[3]=round(1-w[0]-w[1]-w[2], 3)
    return w


# In[ ]:


def calc_weights1(pool, weights, datas, step, n, weight_step, accuracy, value0):
    
    we=[0]*n
    for i in range(0,len(weights),1):
        we[i]=weights[i]
    #print('we= ', we)
    dir = calc_price_directions(pool, weights, datas, step, n, value0)
    #print('dir in calc_weights on start= ', dir)
    count=0
    #print(dir[0][0]/datas[step][dir[1][0]])
    #print(dir[0][n-1]/datas[step][dir[1][n-1]])
    while (dir[0][0]/datas[step][dir[1][0]] > accuracy) and (dir[0][n-1]/datas[step][dir[1][n-1]]<(-accuracy) and count<1000 ): 
        #print('count=', count)
        we[dir[1][0]]=we[dir[1][0]]-weight_step
        we[dir[1][n-1]]=we[dir[1][n-1]]+weight_step
        #print('we in progress= ', we)
        dir = calc_price_directions(pool, we, datas, step, n, value0)
        #print('dir in calc weights', dir)
        count=count+1
    return we


# In[ ]:


def frange(start, end, step=0.1):
    i = start
    while i < end:
        yield i
        i += step


# In[ ]:


def delta_spot_market_usd1(pool, weights, datas, step, n, value0):
    d=[0]*n
    sp=spot_price_usd(pool, weights, datas, step, n, value0)
    #print('sp = ', sp)
    mp=market_price_usd(datas, step, n)
    #print('mp = ', mp)
    for i in range(0,n,1):
        d[i]=(sp[i]-mp[i])/mp[i]
    return d


# In[ ]:


def calc_price_directions1(pool, weights, datas, step, n, value0):
    #d0=delta_spot_market_usd(pool, weights, datas, step, n, value0)
    d=delta_spot_market_usd1(pool, weights, datas, step, n, value0)
    #print('delta0=', d0 )
    #print('delta= ', d )
    arr=[0]*len(d)
    for i in range(0,len(d)):
        arr[i]=(d[i])/datas[step][i]
    print('arr=', arr )
    arr1=sorted(arr, reverse = True)
    
    pos=[-1]*n
    for i in range (0,n,1):
        for j in range (0,n,1):
            if arr1[i] == arr[j]:
                pos[i]=j
    #print(pos)
    d1=sorted(d, reverse = True)
    return [d1,pos]


# In[1]:


def calc_price_directions2(pool, weights, datas, step, n, value0):
    #d0=delta_spot_market_usd(pool, weights, datas, step, n, value0)
    d=delta_spot_market_usd(pool, weights, datas, step, n, value0)
    arr=[0]*n
    for i in range (0,n):
        arr[i]=d[i]/datas[step][i]
    max1=max(arr)
    min1=min(arr)
    pos_in=-1
    pos_out=-1
    for i in range(0, n):
        if arr[i]==max1:
            pos_in=i 
        if arr[i]==min1:
            pos_out=i 
    return [pos_in,pos_out, d[pos_in], d[pos_out]]#[pos_in,pos_out, d[pos_in], d[pos_out]]


# In[ ]:


def calc_arbitr_one_dir1(pool, weights, datas, step, n, am, accuracy, value0, fee):
    amount_in=0
    amount_out=[0]*4
    amount_in_max=0
    amount_out_max=0
    pool11=[0]*n
    for i in range(0,len(pool),1):
        pool11[i]=pool[i]
    #print('pool on start in calc_amount= ', pool11)
    dir = calc_price_directions2(pool11, weights, datas, step, n, value0)
    #print('calc_price_directions in arbitr_one_dir1= ', dir)
    dir_in = dir[0]
    dir_out = dir[1]
    #print('dir_in, dir_out in calc_amount_one= ', dir_in, dir_out)
    profit_max=0
    count=0
    amount_step=0
    if pool[dir_in]<100:
        amount_step=0.1
    elif pool[dir_in]<1000:
        amount_step=1
    elif pool[dir_in]<10000:
        amount_step=10
    elif pool[dir_in]<1000000:
        amount_step=100
    else:
        amount_step=1000
    if (dir[2]/datas[step][dir_in] > 0) and (dir[3]/datas[step][dir_out]<0):
        while (dir[2]/datas[step][dir_in] > 0) and (dir[3]/datas[step][dir_out]<0 and count<1000 and dir_out==dir[1] and dir_in==dir[0]): 
            amount_in=amount_in+amount_step
            amount_out = calc_out_given_in(pool11, weights, fee, amount_in, dir_in, dir_out, n)
            #print('in/out', amount_in,' ', amount_out[3])
            pr = amount_out[3]*datas[step][dir_out] - amount_in*datas[step][dir_in]
            #print('pr=', pr)
            if  pr>0 and profit_max>=0 and pr>profit_max:
                pool11[dir_in]=pool[dir_in]+amount_in
                pool11[dir_out]=pool[dir_out]-amount_out[3]
                profit_max=pr
                amount_in_max=amount_in
                amount_out_max=amount_out[3]
                #print(count, ' pool = ', pool11)
            dir = calc_price_directions2(pool11, weights, datas, step, n, value0)
            #print('dir in calc_am_one_dir= ', dir)
            count=count+1
            #print('profit arbitr= ', pr)
        #print('profit arbitr= ', profit_max)
    else:
        dir_in=0
        dir_out=0
        amount_out[3]=0
    return  [dir_in, amount_in_max, dir_out, amount_out_max]#[dir_in, amount_in, dir_out, amount_out]


# In[ ]:


def swap_1step_ratio(pool, weights, datas, fee, n, ratio1, index ):#We have pool, weights and get new ratio
    val0=value(pool, datas, index, n)#стоимость пула в момент = index
    pool_new = pool_from_ratio_value(ratio1, datas, index, val0, n)
    weights1= calc_weights(pool_new, weights, datas, index, n, 0.001, 0, val0)
    #calc swap and make swap
    data_for_swap1 = calc_arbitr_one_dir1(pool, weights1, datas, index, n, 0, 0, val0, fee)
    pool1=one_swap(pool, data_for_swap1, fee, n)
    for i in range(0,10,1):
        data_for_swap1 = calc_arbitr_one_dir1(pool1, weights1, datas, index, n, 0, 0, val0, fee)
        #print('data_for_swap1 =', data_for_swap1)
        pool1=one_swap(pool1, data_for_swap1, fee, n)
    #pool_fin1 = pool1
    return [pool1, weights1]


# In[ ]:


def swap_1step_weights(pool, weights, datas, fee, n, weigths1, index ):#We have pool, weights and get new weigths1
    val0=value(pool, datas, index, n)#стоимость пула в момент = index
    #pool_new = pool_from_ratio_value(ratio1, datas, index, val0, n)
    #weights1= calc_weights(pool_new, weights, datas, index, n, 0.001, 0, val0)
    #calc swap and make swap
    data_for_swap1 = calc_arbitr_one_dir1(pool, weights, datas, index, n, 0, 0, val0, fee)
    pool1=one_swap(pool, data_for_swap1, fee, n)
    for i in range(0,10,1):
        data_for_swap1 = calc_arbitr_one_dir1(pool1, weights, datas, index, n, 0, 0, val0, fee)
        #print('data_for_swap1 =', data_for_swap1)
        pool1=one_swap(pool1, data_for_swap1, fee, n)
    #pool_fin1 = pool1
    return [pool1, weights1]

