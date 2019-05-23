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
        :return: True or False
        """

        def myeject(theta, player):
            """
            喷射辅助函数
            :return:
            """
            fx = math.sin(theta)
            fy = math.cos(theta)
            player.veloc[0] -= Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
            player.veloc[1] -= Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
            player.radius *= (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5

        MyNode = boshen(targetcell)  # 此函数为波神的函数
        player = allcells[self.id]
        frame_delta = Consts["FRAME_DELTA"]
        for t in range(MyNode.time):  # 小球运动过程
            theta = MyNode.theta  # 得到的喷射角度
            # 所有球的运动过程
            myeject(theta, player)  # 喷射
            for cell in allcells:
                if not cell.dead:
                    cell.move(frame_delta)
                if cell.id != self.id and cell.radius > player.radius:  # the cells larger than the player
                    if player.collide(cell):
                        return False
        while True:
            for cell in allcells:
                if not cell.dead:
                    cell.move(frame_delta)
                if cell.id != self.id and cell.radius > player.radius:  # the cells larger than the player
                    if player.collide(cell):
                        return False
            if player.collide(targetcell):
                break
        if indanger():  # 此函数为hzy的危险判断函数
            return False
        else:
            return True