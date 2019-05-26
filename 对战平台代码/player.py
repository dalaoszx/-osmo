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
    def __init__(self, id, arg = None):
        self.id = id
        self.finish = True
        self.eject_lst = []
        self.t = 0

    def change_frame(self, cell1, cell2):  # 从地面系换到cell1系，得到新的cell2
        cell3 = Cell()
        cell3.pos[0] = cell2.pos[0] - cell1.pos[0]
        cell3.pos[1] = cell2.pos[1] - cell1.pos[0]
        cell3.veloc[0] = cell2.veloc[0] - cell1.veloc[0]
        cell3.veloc[1] = cell2.veloc[1] - cell1.veloc[1]
        cell3.radius = cell2.radius
        return cell3

    def polar_frame(self, cell1, cell2):  # 从地面系换到cell1系，得到新的极坐标的cell2，其中pos=[r，theta], veloc=[v_r,v_theta]
        cell3 = self.change_frame(cell1, cell2)
        x = cell3.pos[0]
        y = cell3.pos[1]
        vx = cell3.veloc[0]
        vy = cell3.veloc[1]
        cell3.pos[0] = math.hypot(x, y)
        cell3.pos[1] = math.atan2(x, y)
        cell3.veloc[0] = vy * math.cos(cell3.pos[1]) + vx * math.sin(cell3.pos[1])
        cell3.veloc[1] = -vy * math.sin(cell3.pos[1]) + vx * math.cos(cell3.pos[1])
        return cell3

    def eject(self, theta, cell0):  # 得到发射后在地面系的新的cell,theta为cell系中的发射方向
        fx = math.sin(theta)
        fy = math.cos(theta)
        new_cell = Cell()
        new_cell.veloc[0] = cell0.veloc[0] - Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
        new_cell.veloc[1] = cell0.veloc[1] - Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
        new_cell.radius = cell0.radius * (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5
        new_cell.pos = cell0.pos
        return new_cell

    def chase(self, cell0, cell1, phi=20):
        new_cell = self.polar_frame(cell0, cell1)
        if abs(new_cell.veloc[1] / (Consts['DELTA_VELOC'] * Consts['EJECT_MASS_RATIO'])) > phi or new_cell.veloc[0]>0:
            return None
        elif abs(new_cell.veloc[1]) <= Consts['DELTA_VELOC'] * Consts['EJECT_MASS_RATIO']:
            theta = new_cell.pos[1] - math.copysign(math.pi/2+math.acos(abs(new_cell.veloc[1])/(Consts['DELTA_VELOC'] * Consts['EJECT_MASS_RATIO'])),new_cell.veloc[1])
            if theta > math.pi*2:
                theta -= 2*math.pi
            elif theta < 0:
                theta += 2*math.pi
            return -theta
        else:
            theta = new_cell.pos[1] - math.copysign(math.pi/2,new_cell.veloc[1])
            if theta > math.pi*2:
                theta -= 2*math.pi
            elif theta < 0:
                theta += 2*math.pi
            return -theta

    def chase_income(self, cell0, cell1):
        cell2 = copy.copy(cell0)
        new_cell = self.polar_frame(cell0, cell1)
        if new_cell.veloc[0] > 0:
            return None, None, None
        eject_lst = [0]
        while abs(math.atan2(new_cell.veloc[1], new_cell.veloc[0])) > math.asin((cell0.radius+cell1.radius)/new_cell.pos[0]):
            theta = self.chase(cell0, cell1)
            if theta is None:
                return None, None, None
            cell0 = self.eject(theta, cell0)
            cell0.move(Consts['FRAME_DELTA'])
            cell1.move(Consts['FRAME_DELTA'])
            eject_lst[0] += 1
            eject_lst.append(theta)
            new_cell = self.polar_frame(cell0, cell1)
        if cell1.radius > cell0.radius:
            return None, None, None
        delta_m = -cell2.radius**2 + (cell0.radius**2+cell1.radius**2)
        delta_t = eject_lst[0] + (new_cell.pos[0]-cell0.radius-cell1.radius)/(abs(new_cell.veloc[0])*Consts['FRAME_DELTA'])
        return delta_m/delta_t, eject_lst, int(delta_t)

    def strategy(self, allcells):
        r = 20000
        if self.finish == True:
            max_income = 0
            for cell in allcells:
                if cell != allcells[self.id] and allcells[self.id].distance_from(cell) <= r and cell.radius < allcells[self.id].radius:
                    income, eject_lst, t = self.chase_income(allcells[self.id], cell)
                    print(income)
                    if income is not None and income > max_income:
                        max_income, max_eject, max_t = income, eject_lst, t
            if max_income == 0:
                return None
            else:
                self.eject_lst = max_eject[1:]
                self.t = max_t
                self.finish = False
        else:
            if self.t > 0:
                self.t -= 1
                if len(self.eject_lst) > 0:
                    return self.eject_lst.pop(0)
                else:
                    return None
            else:
                self.finish = True
                return None



