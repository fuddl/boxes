#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Guillaume Collic
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
from functools import partial
from boxes import Boxes


class PaperBox(Boxes):
    """
    Box made of paper, with lid.
    """

    ui_group = "Misc"

    description = """
    This box is made of paper.
    There is marks in the "outside leftover paper" to help see where to fold
    (cutting with tabs helps use them).
    The cut is very precise, and could be too tight if misaligned when glued.
    A plywood box (such as a simple TypeTray) of the same size is a great guide
    during folding and glueing. Just fold the box against it. Accurate quick and
    easy.
    A paper creaser (or bone folder) is also usefull.
    """

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h")

        self.argparser.add_argument(
            "--design",
            action="store",
            type=str,
            default="automatic",
            choices=("automatic", "widebox", "tuckbox"),
            help="different design for paper consumption optimization",
        )

        self.argparser.add_argument(
            "--lid_heigth",
            type=float,
            default=15,
            help="Height of the lid (part which goes inside the box)",
        )
        self.argparser.add_argument(
            "--lid_radius",
            type=float,
            default=7,
            help="Angle, in radius, of the round corner of the lid",
        )
        self.argparser.add_argument(
            "--lid_sides",
            type=float,
            default=20,
            help="Width of the two sides upon which goes the lid",
        )
        self.argparser.add_argument(
            "--margin",
            type=float,
            default=0.5,
            help="Margin for the glued sides",
        )
        self.argparser.add_argument(
            "--mark_length",
            type=float,
            default=1.5,
            help="Length of the folding outside mark",
        )
        self.argparser.add_argument(
            "--tab_angle_rad",
            type=float,
            default=math.atan(2 / 25),
            help="Angle (in radian) of the sides which are to be glued inside the box",
        )

        self.argparser.add_argument(
            "--finger_hole_diameter",
            type=float,
            default=15,
            help="Diameter of the hole to help catch the lid",
        )

    def render(self):
        if self.design == "automatic":
            self.design = "tuckbox" if self.h > self.y else "widebox"

        path = (
            self.tuckbox(self.x, self.y, self.h)
            if self.design == "tuckbox"
            else self.widebox(self.x, self.y, self.h)
        )

        self.polyline(*path)

    def tuckbox(self, width, length, height):
        half_side = (
            self.mark(self.mark_length)
            + [
                0,
                90,
            ]
            + self.dented_tab_description(length)
            + [
                0,
                -90,
                length,
                0,
            ]
            + self.lid_cut(length / 2)
            + self.lid(width)
            + [0]
            + self.lid_cut(length / 2)
            + [
                length,
                -90,
            ]
            + self.dented_tab_description(length, reverse=True)
        )
        return (
            [height, 0]
            + half_side
            + self.side_with_finger_hole(width, self.finger_hole_diameter)
            + self.mark(self.mark_length)
            + [
                0,
                90,
            ]
            + self.tab_description(length - self.margin, height)
            + [
                0,
                90,
            ]
            + self.mark(self.mark_length)
            + [width]
            + list(reversed(half_side))
        )

    def widebox(self, width, length, height):
        half_side = (
            self.mark(self.mark_length)
            + [
                0,
                90,
            ]
            + self.tab_description(length / 2 - self.margin, height)
            + [
                0,
                -90,
                height,
                0,
            ]
            + self.mark(self.mark_length)
            + [
                0,
                90,
            ]
            + self.tab_description(self.lid_sides, length)
            + [
                0,
                90,
            ]
            + self.mark(self.mark_length)
            + [
                height,
                -90,
            ]
            + self.tab_description(length / 2 - self.margin, height)
            + [
                length,
                0,
            ]
            + self.mark(self.mark_length)
        )
        return (
            self.side_with_finger_hole(width, self.finger_hole_diameter)
            + half_side
            + self.lid(width)
            + list(reversed(half_side))
        )

    def lid(self, width):
        return [
            self.lid_heigth - self.lid_radius,
            (90, self.lid_radius),
            width - 2 * self.lid_radius,
            (90, self.lid_radius),
            self.lid_heigth - self.lid_radius,
        ]

    def mark(self, length):
        if length == 0:
            return []
        return [
            0,
            -90,
            length,
            180,
            length,
            -90,
        ]

    def lid_cut(self, length):
        if length == 0:
            return []
        return [
            0,
            90,
            length,
            -180,
            length,
            90,
        ]

    def side_with_finger_hole(self, width, finger_hole_diameter):
        half_width = (width - finger_hole_diameter) / 2

        return [
            half_width,
            90,
            0,
            (-180, finger_hole_diameter / 2),
            0,
            90,
            half_width,
            0,
        ]

    def tab_description(self, height, width):
        deg = math.degrees(self.tab_angle_rad)
        side = height / math.cos(self.tab_angle_rad)
        end_width = width - 2 * height * math.tan(self.tab_angle_rad)
        return [
            0,
            deg - 90,
            side,
            90 - deg,
            end_width,
            90 - deg,
            side,
            deg - 90,
        ]

    def dented_tab_description(self, width, reverse=False):
        deg = math.degrees(self.tab_angle_rad)
        side = width / math.cos(self.tab_angle_rad)
        end_width = width - 2 * width * math.tan(self.tab_angle_rad)
        path = [
            2 * self.burn,
            -90,
            width / 2,
            90,
            0,
            (-90, width / 4),
            width / 4,
            90,
            width - (width / 4) - 4 * self.burn,
            90,
            width,
            -90,
            2 * self.burn,
        ]

        return (list(reversed(path)) if reverse else path) + [0]
