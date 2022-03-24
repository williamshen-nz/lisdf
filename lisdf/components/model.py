#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# File   : model.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 03/23/2022
#
# Distributed under terms of the MIT license.

import numpy as np
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from functools import cached_property
from lisdf.utils.typing import Vector3f
from lisdf.utils.transformations import euler_from_quaternion, quaternion_from_euler
from .base import StringConfigurable
from .control import ControlInfo, JointInfo
from .sensor import Sensor
from .shape import ShapeInfo
from .visual import VisualInfo

__all__ = ['Pose', 'Inertia', 'Inertial', 'Geom', 'Joint', 'Link', 'Model', 'World', 'URDFModel']


@dataclass
class Pose(StringConfigurable):
    pos: Vector3f
    quat_wxyz: Vector3f

    @classmethod
    def from_rpy_6d(cls, a):
        return cls.from_rpy(a[:3], a[3:])

    @classmethod
    def from_rpy(cls, pos, rpy):
        return cls.from_quat_xyzw(pos, quaternion_from_euler(*rpy))

    @classmethod
    def from_quat_xyzw(cls, pos, xyzw):
        return cls(pos, np.array([xyzw[3], xyzw[0], xyzw[1], xyzw[2]]))

    @cached_property
    def quat_xyzw(self):
        return np.array([self.quat_wxyz[1], self.quat_wxyz[2], self.quat_wxyz[3], self.quat_wxyz[0]])

    @cached_property
    def rpy(self):
        return euler_from_quaternion(self.quat_xyzw)

    @classmethod
    def identity(cls):
        return cls(pos=np.zeros(3, dtype='float32'), quat_wxyz=np.array([1, 0, 0, 0], dtype='float32'))


@dataclass
class Inertia(StringConfigurable):
    ixx: float
    ixy: float
    ixz: float
    iyy: float
    iyz: float
    izz: float

    @classmethod
    def zeros(cls):
        return cls(0, 0, 0, 0, 0, 0)

    @classmethod
    def from_diagnal(cls, ixx, iyy, izz):
        return cls(ixx, 0, 0, iyy, 0, izz)

    @property
    def matrix(self):
        return np.array([
            [self.ixx, self.ixy, self.ixz],
            [self.ixy, self.iyy, self.iyz],
            [self.ixz, self.iyz, self.izz],
        ], dtype=np.float32)


@dataclass
class Inertial(StringConfigurable):
    mass: float
    pose: Pose
    inertia: Inertia

    @classmethod
    def zeros(cls):
        return cls(0, Pose.identity(), Inertia.zeros())


@dataclass
class Geom(object):
    name: str
    pose: Pose
    shape: ShapeInfo
    visual: Optional[VisualInfo] = None
    mjcf_configs: Optional[Dict[str, str]] = None

    @property
    def type(self):
        return self.shape.type


@dataclass
class Joint(object):
    name: str
    parent: str
    child: str
    pose: Pose
    joint_info: JointInfo
    control_info: Optional[ControlInfo] = None

    @property
    def type(self):
        return self.joint_info.type

    model: Optional['Model'] = None

    def set_model(self, model):
        self.model = model

    @property
    def parent_link(self):
        return self.model.links[self.parent]

    @property
    def child_link(self):
        return self.model.links[self.child]


@dataclass
class Link(object):
    name: str
    parent: str
    pose: Pose
    inertial: Inertial = None
    collisions: List[Geom] = field(default_factory=list)
    visuals: List[Geom] = field(default_factory=list)
    sensors: List[Sensor] = field(default_factory=list)
    model: Optional['Model'] = None
    # sites: List[Site] = None

    def set_model(self, model):
        self.model = model


@dataclass
class Model(object):
    name: str
    pose: Pose
    parent: Optional[str] = None
    static: Optional[bool] = False

    links: Dict[str, Link] = field(default_factory=list)
    joints: Dict[str, Joint] = field(default_factory=list)


@dataclass
class World(object):
    name: Optional[str] = None
    static: Optional[bool] = False
    models: List[Model] = field(default_factory=list)


@dataclass
class URDFModel(object):
    name: str
    uri: str
    pose: Pose