# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division


from numpy import pi
from numpy import zeros
from numpy import sin
from numpy import cos
from numpy.random import random

from numpy import float32 as npfloat
from numpy import int32 as npint


TWOPI = pi*2
PI = pi



class DifferentialLine(object):

  def __init__(
      self,
      size,
      stp,
      spring_stp,
      reject_stp,
      near_rad,
      far_rad,
      threads = 256,
      nmax = 1000000
    ):

    self.itt = 0

    self.threads = threads
    self.nmax = nmax
    self.size = size

    self.one = 1.0/size
    self.stp = stp
    self.spring_stp = spring_stp
    self.reject_stp = reject_stp
    self.near_rad = near_rad
    self.far_rad = far_rad

    self.__init()
    self.__cuda_init()

  def __init(self):

    self.num = 0

    nz = int(1.0/(2*self.far_rad))

    self.nz = nz
    self.nz2 = nz**2
    nmax = self.nmax

    self.xy = zeros((nmax, 2), npfloat)
    self.dxy = zeros((nmax, 2), npfloat)
    self.tmp = zeros((nmax, 1), npfloat)
    self.link_len = zeros((2*nmax, 1), npfloat)
    self.links = zeros((2*nmax, 1), npint)

    zone_map_size = self.nz2*64
    self.zone_node = zeros(zone_map_size, npint)

    self.zone_num = zeros(self.nz2, npint)

  def __cuda_init(self):

    import pycuda.autoinit
    from helpers import load_kernel

    self.cuda_agg_count = load_kernel(
      'modules/cuda/agg_count.cu',
      'agg_count',
      subs={'_THREADS_': self.threads}
    )

    self.cuda_agg = load_kernel(
      'modules/cuda/agg.cu',
      'agg',
      subs={'_THREADS_': self.threads}
    )
    self.cuda_step = load_kernel(
      'modules/cuda/step.cu',
      'step',
      subs={
        '_THREADS_': self.threads
      }
    )

  def init_circle(self, n, rad):

    from numpy import sort

    num = self.num
    links = self.links

    angles = random(n)*TWOPI
    angles = sort(angles)

    xx = 0.5 + cos(angles)*rad
    yy = 0.5 + sin(angles)*rad

    self.xy[num:num+n, 0] = xx
    self.xy[num:num+n, 1] = yy

    for i in xrange(num+1, num+n-1):
      links[2*i] = i-1
      links[2*i+1] = i+1

    links[2*num+1] = num+1
    links[2*num] = num+n-1
    links[2*(num+n-1)+1] = num
    links[2*(num+n-1)] = num+n-2

    # for i in xrange(num, num+n):
      # print(i, links[2*i: 2*i+2].flatten())

    self.num = num+n

  def spawn(self, limit, prob=0.01, t=None):

    links = self.links
    link_len = self.link_len
    xy = self.xy
    num = self.num

    rnd = random(num)
    mask = (rnd<prob).nonzero()[0]

    if len(mask)<1:
      return

    for i in mask:
      # a = links[2*i]
      b = links[2*i+1,0]

      l = link_len[2*i+1,0]
      if l>limit:

        newxy = (xy[b,:]+xy[i,:])*0.5
        xy[num,:] = newxy

        links[2*i+1] = num
        links[2*num] = i
        links[2*num+1] = b
        links[2*b] = num
        num += 1

    # for i in xrange(self.num):
      # print(i, links[2*i: 2*i+2].flatten(), link_len[2*i: 2*i+2].flatten())

    self.num = num

  def step(self, t=None):

    import pycuda.driver as drv

    self.itt += 1

    num = self.num
    xy = self.xy
    dxy = self.dxy
    tmp = self.tmp
    link_len = self.link_len
    blocks = num//self.threads + 1

    self.zone_num[:] = 0

    self.cuda_agg_count(
      npint(num),
      npint(self.nz),
      drv.In(xy[:num,:]),
      drv.InOut(self.zone_num),
      block=(self.threads,1,1),
      grid=(blocks,1)
    )

    zone_leap = self.zone_num[:].max()
    zone_map_size = self.nz2*zone_leap

    if zone_map_size>len(self.zone_node):
      print('resize, new zone leap: ', zone_map_size*2./self.nz2)
      self.zone_node = zeros(zone_map_size*2, npint)

    self.zone_num[:] = 0

    self.cuda_agg(
      npint(num),
      npint(self.nz),
      npint(zone_leap),
      drv.In(xy[:num,:]),
      drv.InOut(self.zone_num),
      drv.InOut(self.zone_node),
      block=(self.threads,1,1),
      grid=(blocks,1)
    )

    self.cuda_step(
      npint(num),
      npint(self.nz),
      npint(zone_leap),
      drv.In(xy[:num,:]),
      drv.Out(dxy[:num,:]),
      drv.Out(tmp[:num,:]),
      drv.Out(link_len[:num*2,:]),
      drv.In(self.links[:num*2,:]),
      drv.In(self.zone_num),
      drv.In(self.zone_node),
      npfloat(self.stp),
      npfloat(self.reject_stp),
      npfloat(self.spring_stp),
      npfloat(self.near_rad),
      npfloat(self.far_rad),
      block=(self.threads,1,1),
      grid=(blocks,1)
    )

    xy[:num,:] += dxy[:num,:]

