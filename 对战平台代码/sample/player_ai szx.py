#!/usr/bin/env python3

#####################################################
#                                                   #
#     ______        _______..___  ___.   ______     #
#    /  __  \      /       ||   \/   |  /  __  \    #
#   |  |  |  |    |   (----`|  \  /  | |  |  |  |   #
#   |  |  |  |     \   \    |  |\/|  | |  |  |  |   #
#   |  `--'  | .----)   |   |  |  |  | |  `--'  |   #
#    \______/  |_______/    |__|  |__|  \______/    #
#                                                   #
#                                                   #
#####################################################

# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

from consts import Consts
from cell import Cell
import math
import copy


class Player():
    class Node():
        def __init__(self, inittheta=0, inittime=0, initcost=0):
            self.theta = inittheta
            self.time = inittime
            self.cost = initcost
            self.next = None
            self.prev = None

        # next和prev功能在创建链表时候可能使用，在估值时没有用，如果之后用不上可以删除
        def gettheta(self):
            my_theta = math.pi + self.theta
            if my_theta > 2 * math.pi:
                return my_theta - 2 * math.pi
            else:
                return my_theta

        def gettime(self):
            return self.time

        def getcost(self):
            return self.cost

        def getNext(self):
            return self.next

        def getPrev(self):
            return self.prev

        def settheta(self, newdata):
            self.theta = newdata

        def settime(self, newdata):
            self.time = newdata

        def setcost(self, newdata):
            self.cost = newdata

        def setNext(self, newnext):
            self.next = newnext

        def setPrev(self, newprev):
            self.prev = newprev

    def __init__(self, id, arg=None):
        self.id = id
        self.finish = True
        self.t = 0
        self.theta = None
        self.target = None

    def reset(self):
        self.finish = True
        self.t = 0
        self.theta = None
        self.target = None

    class cell_node():
        def __init__(self, id=None, pos=[0, 0], veloc=[0, 0], radius=5):
            self.id = id
            self.pos = pos
            self.veloc = veloc
            self.radius = radius
        # 由于cell类把坐标限制在了一定范围，为实现九个区域分别计算，重新定义一个cell_node类

    def trans(self, cell):
        b = self.cell_node()
        b.id = cell.id
        b.pos = cell.pos
        b.veloc = cell.veloc
        b.radius = cell.radius
        return b
        # 将cell类的基本元素转换到cell_node类

    def getTheBestNode(self, sel, oth):
        id = oth.id
        pos = oth.pos
        veloc = oth.veloc
        radius = oth.radius
        pos_1_1 = pos[0] - Consts["WORLD_X"]
        pos_1_2 = pos[0]
        pos_1_3 = pos[0] + Consts["WORLD_X"]
        pos_2_1 = pos[1] - Consts["WORLD_Y"]
        pos_2_2 = pos[1]
        pos_2_3 = pos[1] + Consts["WORLD_Y"]
        adict = {}
        adict[1] = self.relative_exchange(sel, self.cell_node(id, [pos_1_1, pos_2_3], veloc, radius))
        adict[2] = self.relative_exchange(sel, self.cell_node(id, [pos_1_2, pos_2_3], veloc, radius))
        adict[3] = self.relative_exchange(sel, self.cell_node(id, [pos_1_3, pos_2_3], veloc, radius))
        adict[4] = self.relative_exchange(sel, self.cell_node(id, [pos_1_1, pos_2_2], veloc, radius))
        adict[5] = self.relative_exchange(sel, self.cell_node(id, [pos_1_2, pos_2_2], veloc, radius))
        adict[6] = self.relative_exchange(sel, self.cell_node(id, [pos_1_3, pos_2_2], veloc, radius))
        adict[7] = self.relative_exchange(sel, self.cell_node(id, [pos_1_1, pos_2_1], veloc, radius))
        adict[8] = self.relative_exchange(sel, self.cell_node(id, [pos_1_2, pos_2_1], veloc, radius))
        adict[9] = self.relative_exchange(sel, self.cell_node(id, [pos_1_3, pos_2_1], veloc, radius))
        cost = adict[1].cost
        l = 1
        for i in range(1, 10):
            if adict[i].cost > cost:
                cost = adict[i].cost
                l = i
        return adict[l]

    def relative_exchange(self, sel, oth):  # 输入：自己的坐标，需要追的球坐标，输入类型为cellNode
        relative_pos = [oth.pos[0] - sel.pos[0], oth.pos[1] - sel.pos[1]]  # 计算相对位置
        relative_veloc = [oth.veloc[0] - sel.veloc[0], oth.veloc[1] - sel.veloc[1]]  # 计算相对速度
        alpha2 = 0
        alpha1 = 0
        if relative_veloc[0] == 0:
            if relative_veloc[1] > 0:
                alpha2 = 90
            elif relative_veloc[1] == 0:
                alpha2 = 0
            elif relative_veloc[1] < 0:
                alpha2 = 270
        elif relative_veloc[0] > 0:
            if relative_veloc[1] > 0:
                alpha2 = math.degrees(math.atan(relative_veloc[1] / relative_veloc[0]))  # 计算相对速度角度
            elif relative_veloc[1] < 0:
                alpha2 = math.degrees(math.atan(relative_veloc[1] / relative_veloc[0])) + 360
        else:
            alpha2 = math.degrees(math.atan(relative_veloc[1] / relative_veloc[0])) + 180  # 计算相对速度角度
        d0 = math.sqrt(relative_pos[0] ** 2 + relative_pos[1] ** 2)  # 计算距离
        v0 = math.sqrt(relative_veloc[0] ** 2 + relative_veloc[1] ** 2)  # 计算速度大小
        if relative_pos[0] == 0:
            if relative_pos[1] > 0:
                alpha1 = 90
            elif relative_pos[1] == 0:
                alpha1 = 0
            elif relative_pos[1] < 0:
                alpha1 = 270
        elif relative_pos[0] > 0:
            if relative_pos[1] > 0:
                alpha1 = math.degrees(math.atan(relative_pos[1] / relative_pos[0]))  # 计算相对速度角度
            elif relative_pos[1] < 0:
                alpha1 = math.degrees(math.atan(relative_pos[1] / relative_pos[0])) + 360
        else:
            alpha1 = math.degrees(math.atan(relative_pos[1] / relative_pos[0])) + 180
        # 获取半径信息
        r1 = sel.radius
        r2 = oth.radius
        # 创建输出空节点
        N = self.Node()
        # 创建加速角度范围
        al_inf = int(min(alpha1, alpha2))
        al_sup = int(max(alpha1, alpha2)) + 1
        if al_sup - al_inf > 180:  # 注意，大于180度时将大角减去360度，为了保证区间连续性
            interval = range(al_sup - 360, al_inf + 1)
            delta_alpha = al_inf - al_sup + 360
        else:
            interval = range(al_inf, al_sup + 1)
            delta_alpha = al_sup - al_inf
        for i in interval:  # 遍历喷射角度
            # 下面这个if-else的目的是得到加速方向和相对位置连线的夹角
            if abs(alpha1 - min(interval)) <= 1 or abs(alpha1 - (360 + min(interval))) <= 1:
                relative_i = i - min(interval)
            else:
                relative_i = max(interval) - i
            if relative_i > 90:
                continue
            if abs(relative_i - delta_alpha) < 1:
                continue
            time_i, cost_i = self.cost_of_theta(relative_i, r1, r2, d0, v0, delta_alpha)
            if cost_i > N.cost:  # N.cost默认值是0，也就是说只有大于零才会第一次更新
                if i < 0:
                    i += 360
                i -= 90
                if i < 0:
                    i += 360
                i = 360 - i
                N.settheta((i * math.pi) / 180)  # i是实际加速方向与x轴夹角，不是相对于连线方向的夹角
                N.settime(time_i)
                N.setcost(cost_i)
        return N  # 输出：前进角度、喷射时间、获得收益（cost）

    def F(self, r1, r2, T, t):
        return (r2 ** 2 + (r1 ** 2) * (1 - Consts["EJECT_MASS_RATIO"] * t + 0.5 * t * (t - 1) * Consts[
            "EJECT_MASS_RATIO"] ** 2) - r1 ** 2) / (T)

    def cost_of_theta(self, relative_i, r1, r2, d0, v0, delta_alpha):
        relative_i = math.radians(relative_i)
        delta_alpha = math.radians(delta_alpha)
        time_i = 0
        if r2 >= r1:  # 如果吃不了，那么喷射时间是0，喷射获益是-1
            return 0, -1
        a = (Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"]) / (
                1 - Consts["EJECT_MASS_RATIO"])  # a= 加速度,由帧数以及具体场地细节决定
        # 集体计算方法：使用余弦定理
        d_i = d0 * math.sin(relative_i) / math.sin(delta_alpha - relative_i)
        d_alpha = d0 * math.sin(delta_alpha) / math.sin(delta_alpha - relative_i)
        # 最大喷射时间是{获取收益为0时间，全程加速的时间}也想要加入一个基于经验得出的最多时间
        # t_max = min(int(math.log((r1 ** 2 - r2 ** 2) / r1 ** 2, 1 - Consts["EJECT_MASS_RATIO"])),int(math.sqrt(2 * d_alpha / a)))
        t_max = min(int(math.log((r1 ** 2 - r2 ** 2) / r1 ** 2, 1 - Consts["EJECT_MASS_RATIO"])), 15,
                    int(math.sqrt(2 * d_alpha / a)))
        # 0.99是每次喷出质量
        cost_i = 0
        j = 0.95
        for i in range(0, t_max + 1):
            # AT^2+BT+C==0求解如下，D只是简化进行的换元
            D = d_alpha + 0.5 * a * i ** 2
            A = v0 ** 2 + a ** 2 * i ** 2 - 2 * v0 * a * i * math.cos(delta_alpha - relative_i)
            B = -2 * d_i * v0 - 2 * a * i * D + 2 * (d_i * a * i + D * v0) * math.cos(delta_alpha - relative_i)
            C = d_i ** 2 + D ** 2 - ((r1 + r2) * j) ** 2 - 2 * d_i * D * math.cos(delta_alpha - relative_i)
            # f=(d_i-v0*T)**2 + (d_alpha-a*i*(T-0.5*i))**2 - 2*(d_i-v0*T)*(d_alpha-a*i*(T-0.5*i))*math.cos(delta_alpha-relative_i) - (r2+r1)**2
            # aa=sympy.solve(f,T)
            try:
                a1 = (-B - math.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
            except:
                continue
            else:
                k1 = self.F(r1, r2, a1, i)
                if k1 > cost_i:
                    cost_i = k1
                    time_i = i
        return time_i, cost_i

    def my_asin(self, invalue):
        tmp = math.asin(invalue)
        tmp = math.fabs(tmp)
        return tmp

    def my_atan(self, invx, invy):
        if invy == 0 and invx > 0:
            return 0
        if invy > 0 and invx > 0:
            tmp = math.atan(math.fabs(invy / invx))
            return tmp
        if invx == 0 and invy > 0:
            return math.pi / 2
        if invy > 0 and invx < 0:
            tmp = math.atan(math.fabs(invy / invx))
            return math.pi - tmp
        if invy == 0 and invx < 0:
            return -math.pi
        if invy < 0 and invx < 0:
            tmp = math.atan(math.fabs(invy / invx))
            return tmp + math.pi
        if invx == 0 and invy < 0:
            return 1.5 * math.pi
        if invy < 0 and invx > 0:
            tmp = math.atan(math.fabs(invy / invx))
            return 2 * math.pi - tmp
        if invy == 0 and invx == 0:
            return 999999

    def velocity_angle(self, invx, invy):
        ########如果需要换系，invx，invy相应传入值即可
        return self.my_atan(invx, invy)

    def position_angle(self, thecell1, thecell2):  # 两个cell的方位角
        deltax = thecell2.pos[0] - thecell1.pos[0]
        deltay = -(thecell2.pos[1] - thecell1.pos[1])
        return self.my_atan(deltax, deltay)

    def bound_angle(self, thecell1, thecell2):
        my_r = thecell1.radius
        other_r = thecell2.radius
        distance = thecell1.distance_from(thecell2)
        number = (my_r + other_r) / distance
        if number > 1:
            number = 1  # 防止一个蜜汁bug
        return self.my_asin(number)

    def testisdangerous(self, thecell1, thecell2):
        mytheta = self.bound_angle(thecell1, thecell2)
        mytheta += 1 / 180 * math.pi  # 增加一度对应的弧度，，用于更稳妥的避开
        mybeta = self.position_angle(thecell1, thecell2)
        myalpha = self.velocity_angle(thecell1.veloc[0] - thecell2.veloc[0],
                                      -thecell1.veloc[1] + thecell2.veloc[1])  ####已经换过系，在对方不动系
        if mybeta - mytheta < 0:  ###上界记为myceil，下界记为myfloor
            myceil = 2 * math.pi - (mytheta - mybeta)  ##这一块ceil和floor整体写反了但是不影响
            myfloor = mybeta + mytheta
            if (myalpha > myceil and myalpha < 2 * math.pi) or (myalpha >= 0 and myalpha < myfloor):
                return True
        elif mybeta + mytheta > 2 * math.pi:
            myfloor = mybeta - mytheta
            myceil = mybeta + mytheta - 2 * math.pi
            if (myalpha > myfloor and myalpha < 2 * math.pi) or (myalpha >= 0 and myalpha < myceil):
                return True
        else:
            myfloor = mybeta - mytheta
            myceil = mybeta + mytheta
            if myalpha > myfloor and myalpha < myceil:
                return True
        return False

    def dangerouscelllst(self, allcells):
        adjacentcells = []
        dangerouscells = []
        n = 7
        for acell in allcells:
            if (not acell.dead) and acell != allcells[self.id]:
                if acell.radius > allcells[self.id].radius and allcells[self.id].distance_from(acell) - allcells[
                    self.id].radius - acell.radius < n * Consts["FRAME_DELTA"] * math.hypot(
                    allcells[self.id].veloc[0] - acell.veloc[0], allcells[self.id].veloc[1] - acell.veloc[1]):
                    adjacentcells.append(acell)
        for acell in allcells:
            if (not acell.dead) and acell != allcells[self.id]:
                if acell in adjacentcells and self.testisdangerous(allcells[self.id], acell):
                    dangerouscells.append(acell)
        return dangerouscells

    def is_strategy_available(self, targetcell, MyNode, allcells_copy):
        """
        判断追逐一个目标targetcell的过程中是否会被吞噬，以及结束后是否处于危险
        :param targetcell: 追逐的目标
        :param allcells: allcells
        :return:
        0：途中被大球吃掉或结束后危险
        1：目标被碰撞且不是和玩家相碰
        2：玩家吃到一个新球，但不是目标球
        3：可以吃到且不会危险
        """

        def myeject(theta, player):
            """
            喷射辅助函数
            功能：计算玩家喷射后的速度和半径
            :return:
            """
            fx = math.sin(theta)
            fy = math.cos(theta)
            player.veloc[0] -= Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
            player.veloc[1] -= Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
            player.radius *= (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5

        def myabsorb(allcells_copy, collision):
            """
            吸收辅助函数
            功能：对一个特定碰撞，得到碰撞结果（球存活与死亡，最大球大小速度）
            Args:
                collision: 所有参与一次（多体）碰撞的球的列表
            Returns:


            """
            # 总质量和总动量
            mass = sum(allcells_copy[ele].area() for ele in collision)
            px = sum(allcells_copy[ele].area() * allcells_copy[ele].veloc[0] for ele in collision)
            py = sum(allcells_copy[ele].area() * allcells_copy[ele].veloc[1] for ele in collision)
            # 判断哪个是最大的球，保留，其余死亡
            collision.sort(key=lambda ele: allcells_copy[ele].radius)
            biggest = collision.pop()
            allcells_copy[biggest].radius = (mass / math.pi) ** 0.5
            allcells_copy[biggest].veloc[0] = px / mass
            allcells_copy[biggest].veloc[1] = py / mass
            for ele in collision:
                allcells_copy[ele].dead = True

        def myupdate(player, allcells_copy, frame_delta, mytick, eject_time, theta):
            """
            模拟每一帧运行的辅助函数，mytick用以决定玩家是否喷射
            :param allcells:
            :param frame_delta:
            :param mytick: 记录帧数（以开始判断为零点）
            :param eject_time: 总的喷射时间
            :return:
            """
            # 模拟移动（对存活球）
            for cell in allcells_copy:
                cell.collide_group = None
                if not cell.dead:
                    cell.move(frame_delta)
            # 检测碰撞（包括多体）
            collisions = []
            for i in range(len(allcells_copy)):
                if allcells_copy[i].dead:
                    continue
                for j in range(i + 1, len(allcells_copy)):
                    if not allcells_copy[j].dead and allcells_copy[i].collide(allcells_copy[j]):
                        if allcells_copy[i].collide_group == None == allcells_copy[j].collide_group:
                            allcells_copy[i].collide_group = allcells_copy[j].collide_group = len(collisions)
                            collisions.append([i, j])
                        elif allcells_copy[i].collide_group != None == allcells_copy[j].collide_group:
                            collisions[allcells_copy[i].collide_group].append(j)
                            allcells_copy[j].collide_group = allcells_copy[i].collide_group
                        elif allcells_copy[i].collide_group == None != allcells_copy[j].collide_group:
                            collisions[allcells_copy[j].collide_group].append(i)
                            allcells_copy[i].collide_group = allcells_copy[j].collide_group
                        elif allcells_copy[i].collide_group != allcells_copy[j].collide_group:
                            collisions[allcells_copy[i].collide_group] += collisions[allcells_copy[j].collide_group]
                            for ele in collisions[allcells_copy[j].collide_group]:
                                allcells_copy[ele].collide_group = allcells_copy[i].collide_group
                            collisions[allcells_copy[j].collide_group] = []
            # 对每个碰撞事件执行吸收操作
            for collision in collisions:
                if collision != []:
                    myabsorb(allcells_copy, collision)
            # 执行喷射操作
            if mytick <= eject_time:
                myeject(theta, player)

        # 函数主体
        # MyNode = self.boshen(targetcell)  # 此函数为波神的函数
        player = allcells_copy[self.id]  # 玩家自己
        init_radius = player.radius
        theta = MyNode.gettheta()  # 得到的喷射角度
        eject_time = MyNode.gettime()  # 得到喷射时间
        mytick = 0  # 初始帧
        maxtick = 50  # 最大帧
        frame_delta = Consts["FRAME_DELTA"]
        while 1:
            mytick += 1
            if mytick > maxtick:
                return 0
            myupdate(player, allcells_copy, frame_delta, mytick, eject_time, theta)  # 计算一帧整个画面的运动（认为对手不喷）
            if player.dead:  # 玩家自己死亡，返回false
                return 0
            if targetcell.collide_group != None and targetcell.collide_group != player.collide_group:  # 目标被碰撞且不是和玩家相碰
                return 1

            if player.collide_group != None and targetcell.collide_group != player.collide_group:  # 玩家吃到一个新球，但不是目标球
                if player.radius > init_radius:
                    return 2
                else:
                    return 0
            if player.collide_group != None and targetcell.collide_group == player.collide_group:  # 玩家吃到目标球
                break
        if len(self.dangerouscelllst(allcells_copy)) > 0:
            return 0
        else:
            return 3

    def avoid(self, cell0, cell1):  # cell0是自己，cell1是大球
        theta = math.atan2(cell1.pos[0] - cell0.pos[0], cell1.pos[1] - cell0.pos[1])
        if theta < 0:
            theta = theta + 2 * math.pi
        elif theta > 2 * math.pi:
            theta = theta - 2 * math.pi
        return theta

    def strategy(self, allcells):
        for cell in allcells:
            if cell in self.dangerouscelllst(allcells):
                self.reset()
                return self.avoid(allcells[self.id], cell)
        r = 100-len(allcells)*0.6
        if self.finish:
            strategylst = []
            for cell in allcells:
                if cell.distance_from(allcells[self.id])-allcells[self.id].radius-cell.radius < r and cell != allcells[
                    self.id] and not cell.dead and cell.radius < allcells[self.id].radius and cell.radius > 0.3 * \
                        allcells[self.id].radius:
                    # cellnode = self.getTheBestNode(allcells[self.id], self.trans(cell))
                    cellnode = self.relative_exchange(allcells[self.id], cell)
                    # print(cellnode.getcost())
                    if cellnode.getcost() > 0:
                        strategylst.append((cell, cellnode))
            if len(strategylst) == 0:
                return None
            else:
                strategylst.sort(key=lambda strate: strate[1].getcost(), reverse=True)
            print('length')
            print(len(strategylst))
            for strate in strategylst:
                allcells_copy = copy.copy(allcells)
                target_id = allcells_copy.index(strate[0])
                targetcell = allcells_copy[target_id]
                a = self.is_strategy_available(targetcell, strate[1], allcells_copy)
                print(a)
                if a >= 1:
                    self.target = strate[0].id
                    self.finish = False
                    self.t = strate[1].gettime()
                    self.theta = strate[1].gettheta()
                    print(strate[1].getcost(), strate[1].gettime())
                    break
            else:
                return None
            if self.t == 0:
                return None
            else:
                self.t -= 1
                return self.theta
        else:
            print('aabb')
            if allcells[self.id].collide_group is not None:
                print('a')
                self.reset()
                return None
            i = 0
            for cell in allcells:
                if cell.id == self.target:
                    i = 1
                    if cell.collide_group is not None:
                        print('b')
                        self.reset()
                        return None
            if i == 0:
                print('c')
                self.reset()
                return None

            if self.t > 0:
                self.t -= 1
                return self.theta
            else:
                return None
