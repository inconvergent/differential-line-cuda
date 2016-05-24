#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import print_function
from __future__ import division


def get_wrap(dl, colors, limit, prob, render_steps=10, export_steps=10):

  from fn import Fn
  from time import time
  from modules.helpers import link_sort
  # from dddUtils.ioOBJ import export_2d as export

  t0 = time()

  fn = Fn(prefix='./res/')

  def wrap(render):

    dl.step()
    # dl.spawn_curl(limit=limit, prob=prob)
    dl.spawn_normal(limit=limit, prob=prob)

    if dl.itt % render_steps == 0:

      print('itt', dl.itt, 'num', dl.num, 'time', time()-t0)

      num = dl.num

      render.clear_canvas()
      render.set_line_width(dl.one)

      xy = dl.xy[:num,:]
      links = dl.links[:2*num,0]

      render.ctx.set_source_rgba(*colors['front'])

      ## dots
      # for x,y in xy:
        # render.circle(x, y, dl.one, fill=True)

      ## edges
      # for i in xrange(num):
        # # a = links[2*i]
        # b = links[2*i+1]
        # render.line(xy[i,0], xy[i,1], xy[b,0], xy[b,1])

      ## connected edges
      ov = link_sort(links)
      remapped = xy[ov,:]
      render.ctx.move_to(remapped[0,0], remapped[0,1])
      for x in remapped[:,:]:
        render.ctx.line_to(x[0], x[1])
      render.ctx.fill()

    if dl.itt % export_steps == 0:

      name = fn.name()
      render.write_to_png(name+'.png')
      # export('lattice', name+'.2obj', vertices, edges=edges)

    return True

  return wrap



def main():

  from modules.differentialLine import DifferentialLine
  from render.render import Animate

  colors = {
    'back': [1,1,1,1],
    'front': [0,0,0,0.6],
    'cyan': [0,0.6,0.6,0.6],
    'light': [0,0,0,0.2],
  }

  threads = 512

  render_steps = 3
  export_steps = 3

  size = 512
  one = 1.0/size

  init_num = 200
  init_rad = 0.25

  stp = one*0.4
  spring_stp = 1.0
  reject_stp = 1.0

  near_rad = one*3
  far_rad = 30.*one

  spawn_limit = near_rad
  spawn_prob = 0.1

  DL = DifferentialLine(
    size,
    stp,
    spring_stp,
    reject_stp,
    near_rad,
    far_rad,
    threads = threads
  )

  DL.init_circle(init_num, init_rad)

  wrap = get_wrap(
    DL,
    colors,
    spawn_limit,
    spawn_prob,
    export_steps=export_steps,
    render_steps=render_steps
  )

  render = Animate(size, colors['back'], colors['front'], wrap)
  render.start()


if __name__ == '__main__':

  main()

