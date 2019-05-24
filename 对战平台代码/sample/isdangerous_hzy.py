#adjacentcells列表储存200以内的且比自己巨的cells
#dangerouscells列表 对自己有危险的cells
#my_asin()让返回值只是正值
#my_atan()都是改变过值域的反三角函数
#velocity_angle()返回自己的速度角弧度
#position_angle()返回方位角弧度
#bound_angle()返回恰好相切的临界角弧度，并且永远是正值
#testisdangerous()返回bool,需要if来越界检测,分类讨论
#自己先用me表示

#角度有mytheta（临界角）,myalpha(速度角)，mybeta(方位角)

######me到时候是需要改成真实的自己
import cell
import math
adjacentcells=[]
dangerouscells=[]

for acell in allcells:###allcells按理说是world里面的定义好的
    if not acell.dead:
        if me.distance_from(acell)<200:
            adjacentcells.append(acell)

my_r=me.radius#我方半径
#用other_r作为敌方半径形参

def my_asin(invalue):
    tmp=math.asin(invalue)
    tmp=math.fabs(tmp)
    return tmp

def my_atan(invx,invy):
    if invy==0 and invx>0:
        return 0
    if invy>0 and invx>0:
        tmp=math.atan(math.fabs(invy/invx))
        return tmp
    if invx==0 and invy>0:
        return math.pi/2
    if invy>0 and invx<0:
        tmp=math.atan(math.fabs(invy/invx))
        return math.pi-tmp
    if invy==0 and invx<0:
        return -math.pi
    if invy<0 and invx<0:
        tmp=math.atan(math.fabs(invy/invx))
        return tmp+math.pi
    if invx==0 and invy<0:
        return 1.5*math.pi
    if invy<0 and invx>0:
        tmp=math.atan(math.fabs(invy/invx))
        return 2*math.pi-tmp
    if invx==0 and invy==0:
        return 999999##这样在后面的is_dangerous检测，if的判断都是False
    
def velocity_angle(invx,invy):
    ########如果需要换系，invx，invy相应传入值即可
    return my_atan(invx,invy)

def position_angle(thecell1,thecell2):#两个cell的方位角
    deltax=thecell2.pos[0]-thecell1.pos[0]
    deltay=-(thecell2.pos[1]-thecell1.pos[1])###把y的正方向调整一下
    return my_atan(deltax,deltay)

def bound_angle(thecell1,thecell2):
    my_r=thecell1.radius
    other_r=thecell2.radius
    distance=thecell1.distance_from(thecell2)
    number=(my_r+other_r)/distance
    return my_asin(number)


def testisdangerous(thecell1,thecell2):
    mytheta=bound_angle(thecell1,thecell2)
    mytheta+=1/180*math.pi#增加一度对应的弧度，，用于更稳妥的避开
    mybeta=position_angle(thecell1,thecell2)
    myalpha=velocity_angle(thecell1.veloc[0]-thecell2.veloc[0],-(thecell1.veloc[1]-thecell2.veloc[1]))####已经换过系，在对方不动系,正方向问题，这里y方向加个负号
    if mybeta-mytheta<0:###上界记为myceil，下界记为myfloor
        myceil=2*math.pi-(mytheta-mybeta)##这一块ceil和floor整体写反了但是不影响
        myfloor=mybeta+mytheta
        if (myalpha>myceil and myalpha<2*math.pi) or (myalpha>=0 and myalpha<myfloor):
            return True
    elif mybeta+mytheta>2*math.pi:
        myfloor=mybeta-mytheta
        myceil=mybeta+mytheta-2*math.pi
        if (myalpha>myfloor and myalpha<2*math.pi) or (myalpha>=0 and myalpha<myceil):
            return True
    else:
        myfloor=mybeta-mytheta
        myceil=mybeta+mytheta
        if myalpha>myfloor and myalpha<myceil:
            return True
    return False
    



#循环，检测每个adjacentcells里的cell是否dangerous
for acell in allcells:
    if not acell.dead:
        if testisdangerous(me,acell):
            dangerouscells.append(acell)

##结束


