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


class Player():
    def __init__(self, id, arg=None):
        self.id = id

    def strategy(self, allcells):
        pass

    def is_strategy_available(self, targetcell, allcells):
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

        def myabsorb(allcells, collision):
            """
            吸收辅助函数
            功能：对一个特定碰撞，得到碰撞结果（球存活与死亡，最大球大小速度）
            Args:
                collision: 所有参与一次（多体）碰撞的球的列表
            Returns:


            """
            # 总质量和总动量
            mass = sum(allcells[ele].area() for ele in collision)
            px = sum(allcells[ele].area() * allcells[ele].veloc[0] for ele in collision)
            py = sum(allcells[ele].area() * allcells[ele].veloc[1] for ele in collision)
            # 判断哪个是最大的球，保留，其余死亡
            collision.sort(key=lambda ele: allcells[ele].radius)
            biggest = collision.pop()
            allcells[biggest].radius = (mass / math.pi) ** 0.5
            allcells[biggest].veloc[0] = px / mass
            allcells[biggest].veloc[1] = py / mass
            for ele in collision:
                allcells[ele].dead = True

        def myupdate(player, allcells, frame_delta, mytick, eject_time, theta):
            """
            模拟每一帧运行的辅助函数，mytick用以决定玩家是否喷射
            :param allcells:
            :param frame_delta:
            :param mytick: 记录帧数（以开始判断为零点）
            :param eject_time: 总的喷射时间
            :return:
            """
            # 模拟移动（对存活球）
            for cell in allcells:
                cell.collide_group = None
                if not cell.dead:
                    cell.move(frame_delta)
            # 检测碰撞（包括多体）
            collisions = []
            for i in range(len(allcells)):
                if allcells[i].dead:
                    continue
                for j in range(i + 1, len(allcells)):
                    if not allcells[j].dead and allcells[i].collide(allcells[j]):
                        if allcells[i].collide_group == None == allcells[j].collide_group:
                            allcells[i].collide_group = allcells[j].collide_group = len(collisions)
                            collisions.append([i, j])
                        elif allcells[i].collide_group != None == allcells[j].collide_group:
                            collisions[allcells[i].collide_group].append(j)
                            allcells[j].collide_group = allcells[i].collide_group
                        elif allcells[i].collide_group == None != allcells[j].collide_group:
                            collisions[allcells[j].collide_group].append(i)
                            allcells[i].collide_group = allcells[j].collide_group
                        elif allcells[i].collide_group != allcells[j].collide_group:
                            collisions[allcells[i].collide_group] += collisions[allcells[j].collide_group]
                            for ele in collisions[allcells[j].collide_group]:
                                allcells[ele].collide_group = allcells[i].collide_group
                            collisions[allcells[j].collide_group] = []
            # 对每个碰撞事件执行吸收操作
            for collision in collisions:
                if collision != []:
                    myabsorb(allcells, collision)
            # 执行喷射操作
            if mytick <= eject_time:
                myeject(theta, player)

        # 函数主体
        MyNode = self.boshen(targetcell)  # 此函数为波神的函数
        player = allcells[self.id]  # 玩家自己
        theta = MyNode.theta  # 得到的喷射角度
        eject_time = MyNode.time  # 得到喷射时间
        mytick = 0  # 初始帧
        maxtick = 100  # 最大帧
        frame_delta = Consts["FRAME_DELTA"]
        while 1:
            mytick += 1
            if mytick > maxtick:
                return 0
            myupdate(player, allcells, frame_delta, mytick, eject_time, theta)  # 计算一帧整个画面的运动（认为对手不喷）
            if player.dead:  # 玩家自己死亡，返回false
                return 0
            if targetcell.collide_group != None and targetcell.collide_group != player.collide_group:  # 目标被碰撞且不是和玩家相碰
                return 1
            if player.collide_group != None and targetcell.collide_group != player.collide_group:  # 玩家吃到一个新球，但不是目标球
                return 2
            if player.collide_group != None and targetcell.collide_group == player.collide_group:  # 玩家吃到目标球
                break
        if player.isdanger(allcells):
            return 0
        else:
            return 3

