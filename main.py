#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import print_function
from __future__ import division



def get_wrap(dl, colors, limit, prob, export_steps=10):

  from numpy import pi
  from fn import Fn
  from modules.timers import named_sub_timers
  from time import sleep
  # from dddUtils.ioOBJ import export_2d as export


  twopi = pi*2

  t = named_sub_timers('dl')
  t = None

  # fn = Fn(prefix='./res/')

  def wrap(render):

    dl.step(t)
    dl.spawn(limit=limit, prob=prob, t=t)

    if t:
      t.t('spwn')

    if not dl.itt % export_steps == 0:
      return True

    print('itt', dl.itt, 'num', dl.num)
    if t:
      t.p()

    num = dl.num
    print(num)

    render.clear_canvas()
    render.set_line_width(dl.one)

    xy = dl.xy[:num,:]
    links = dl.links[:2*num,0]

    render.ctx.set_source_rgba(*colors['front'])

    # for x,y in xy:
      # render.circle(x, y, dl.one*2, fill=True)

    for i in xrange(num):
      # a = links[2*i]
      b = links[2*i+1]
      render.line(xy[i,0], xy[i,1], xy[b,0], xy[b,1])

    # name = fn.name()
    # render.write_to_png(name+'.png')
    # export('lattice', name+'.2obj', vertices, edges=edges)

    return True

  return wrap



def main():

  from numpy import array
  from modules.differentialLine import DifferentialLine
  from render.render import Animate

  colors = {
    'back': [1,1,1,1],
    'front': [0,0,0,0.7],
    'cyan': [0,0.6,0.6,0.6],
    'light': [0,0,0,0.2],
  }

  threads = 256
  zone_leap = 1000

  export_steps = 50

  size = 1000
  one = 1.0/size

  init_num = 40

  stp = one*0.5
  spring_stp = 1.0
  reject_stp = 1.0

  spawn_limit = 2.0*one
  spawn_prob = 0.1

  near_rad = one
  far_rad = 30.*one

  DL = DifferentialLine(
    size,
    stp,
    spring_stp,
    reject_stp,
    near_rad,
    far_rad,
    threads = threads,
    zone_leap = zone_leap
  )

  DL.init_circle(init_num, 25*one)

  render = Animate(
    size,
    colors['back'],
    colors['front'],
    get_wrap(DL, colors, spawn_limit, spawn_prob, export_steps)
  )
  render.start()


if __name__ == '__main__':

  main()

