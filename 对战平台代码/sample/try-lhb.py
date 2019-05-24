import sympy
import math
#测试用代码，具体见judge-lhb
def cost_of_theta(relative_i,r1,r2,d0,v0,delta_alpha):
    relative_i=math.radians(relative_i)
    delta_alpha=math.radians(delta_alpha)
    if r2>=r1:
        return 0,-1
    a=0.06    #a= 加速度,由帧数以及具体场地细节决定
    d_i=d0*math.sin(relative_i)/math.sin(delta_alpha-relative_i)
    d_alpha=d0*math.sin(delta_alpha)/math.sin(delta_alpha-relative_i)
    t_max=min(int(math.log((r1**2-r2**2)/r1**2,0.99)),20,int(math.sqrt(2*d_alpha/a)))
    T=sympy.symbols('T')
    t=sympy.symbols('t')
    F=(r2**2+(r1**2)*(0.99**t)-r1**2)/(T)
    time_i=0
    cost_i=0
    for i in range(0,t_max+1):
        D=d_alpha+0.5*a*i**2
        A=v0**2+a**2*i**2-2*v0*a*i*math.cos(delta_alpha-relative_i)
        B=-2*d_i*v0-2*a*i*D+2*(d_i*a*i+D*v0)*math.cos(delta_alpha-relative_i)
        C=d_i**2+D**2-(r1+r2)**2-2*d_i*D*math.cos(delta_alpha-relative_i)
        #f=(d_i-v0*T)**2 + (d_alpha-a*i*(T-0.5*i))**2 - 2*(d_i-v0*T)*(d_alpha-a*i*(T-0.5*i))*math.cos(delta_alpha-relative_i) - (r2+r1)**2
        #aa=sympy.solve(f,T)
        '''
        aa=[]
        aa.append((-B+math.sqrt(B**2-4*A*C))/(2*A))
        aa.append((-B-math.sqrt(B**2-4*A*C))/(2*A))
        resol=0
        for j in aa:
            k=F.subs({T:j,t:i})
            if k>resol:
                resol=k
        if resol>cost_i:
            cost_i=resol
            time_i=i
        '''
        a1=(-B-math.sqrt(B**2-4*A*C))/(2*A)
        k1=F.subs({T:a1,t:i})
        if k1>cost_i:
            cost_i=k1
            time_i=i

            
    return time_i , cost_i
c=0
c1=0
c2=0
for relative_i in range(0,20):
    time_i,cost_i=cost_of_theta(relative_i,5,3.5,10,0.1,179)
    if cost_i>c:
        c2=relative_i
        c1=time_i
        c=cost_i
print(c,c1,c2)



