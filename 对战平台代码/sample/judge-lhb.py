import math
import sympy
'''
注意:所给的角度不是喷射角度，而是加速方向，也就是说喷射角度和这个角度方向相反

目前版本缺失方程无解报错功能
想要调试计算代价的函数可以使用try

'''
class Node():
    def __init__(self, inittheta=0, inittime=0,initcost=0):
        self.theta = inittheta
        self.time = inittime
        self.cost = initcost
        self.next = None
        self.prev = None
#next和prev功能在创建链表时候可能使用，在估值时没有用，如果之后用不上可以删除
    def gettheta(self):
        return self.theta

    def gettime(self):
        return self.time
    
    def getcost(self):
        return self.cost

    def getNext(self):
        return self.next

    def getPrev(self):
        return self.prev

    def settheta(self,newdata):
        self.theta=newdata

    def settime(self,newdata):
        self.time=newdata
    
    def setcost(self,newdata):
        self.cost=newdata

    def setNext(self, newnext):
        self.next = newnext

    def setPrev(self, newprev):
        self.prev = newprev

def relative_exchange(sel,oth):#输入：自己的坐标，需要追的球坐标，输入类型为cellNode
    relative_pos=[oth.pos[0]-sel.pos[0],oth.pos[1]-sel.pos[1]]#计算相对位置
    relative_veloc=[oth.veloc[0]-sel.veloc[0],oth.veloc[1]-sel.veloc[1]]#计算相对速度
    alpha1=math.degrees(math.atan(relative_pos[1]/relative_pos[0]))+90#计算相对位置角度
    alpha2=math.degrees(math.atan(relative_veloc[1]/relative_veloc[0]))+90#计算相对速度角度
    d0=math.sqrt(relative_pos[0]**2+relative_pos[1]**2)#计算距离
    v0=math.sqrt(relative_veloc[0]**2+relative_veloc[1]**2)#计算速度大小
    #下两个if的目的是讲alpha1与alpha2换成0-360的主值区间
    if relative_pos[0]<0:
        alpha1+=180
    if relative_veloc[0]<0:
        alpha2+=180
    #获取半径信息
    r1=sel.radius
    r2=oth.radius
    #创建输出空节点
    N=Node()
    #创建加速角度范围
    al_inf=int(min(alpha1,alpha2))
    al_sup=int(max(alpha1,alpha2))+1
    if al_sup-al_inf>180:#注意，大于180度时将大角减去360度，为了保证区间连续性
        interval=range(al_sup-360,al_inf+1)
        delta_alpha=al_inf-al_sup+360
    else:
        interval=range(al_inf,al_sup+1)
        delta_alpha=al_sup-al_inf
    for i in interval:#遍历喷射角度
        #下面这个if-else的目的是得到加速方向和相对位置连线的夹角
        if abs(alpha1-min(interval))<=1 or abs(alpha1-(360+min(interval)))<=1:
            relative_i=i-min(interval)
        else:
            relative_i=max(interval)-i
        time_i,cost_i=cost_of_theta(relative_i,r1,r2,d0,v0,delta_alpha)
        if cost_i>N.cost:#N.cost默认值是0，也就是说只有大于零才会第一次更新
            N.settheta(i)#i是实际加速方向与x轴夹角，不是相对于连线方向的夹角
            N.settime(time_i)
            N.setcost(cost_i)
    return N #输出：前进角度、喷射时间、获得收益（cost）
        

def cost_of_theta(relative_i,r1,r2,d0,v0,delta_alpha):
    relative_i=math.radians(relative_i)
    delta_alpha=math.radians(delta_alpha)
    if r2>=r1:#如果吃不了，那么喷射时间是0，喷射获益是-1
        return 0,-1
    a=0.6    #a= 加速度,由帧数以及具体场地细节决定
    #集体计算方法：使用余弦定理
    d_i=d0*math.sin(relative_i)/math.sin(delta_alpha-relative_i)
    d_alpha=d0*math.sin(delta_alpha)/math.sin(delta_alpha-relative_i)
    #最大喷射时间是{获取收益为0时间，全程加速的时间}也想要加入一个基于经验得出的最多时间
    t_max=min(int(math.log((r1**2-r2**2)/r1**2,0.99)),int(math.sqrt(2*d_alpha/a)))
    #0.99是每次喷出质量
    T=sympy.symbols('T')
    t=sympy.symbols('t')
    F=(r2**2+(r1**2)*(0.99**t)-r1**2)/(T)
    cost_i=0
    for i in range(0,t_max+1):
        #AT^2+BT+C==0求解如下，D只是简化进行的换元
        D=d_alpha+0.5*a*i**2
        A=v0**2+a**2*i**2-2*v0*a*i*math.cos(delta_alpha-relative_i)
        B=-2*d_i*v0-2*a*i*D+2*(d_i*a*i+D*v0)*math.cos(delta_alpha-relative_i)
        C=d_i**2+D**2-(r1+r2)**2-2*d_i*D*math.cos(delta_alpha-relative_i)
        #f=(d_i-v0*T)**2 + (d_alpha-a*i*(T-0.5*i))**2 - 2*(d_i-v0*T)*(d_alpha-a*i*(T-0.5*i))*math.cos(delta_alpha-relative_i) - (r2+r1)**2
        #aa=sympy.solve(f,T)
        a1=(-B-math.sqrt(B**2-4*A*C))/(2*A)
        k1=F.subs({T:a1,t:i})
        if k1>cost_i:
            cost_i=k1
            time_i=i
    return time_i , cost_i
