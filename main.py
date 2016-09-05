#!/usr/bin/python3
# -*- coding: utf-8 -*-



def get_wrap(dl, colors, limit, prob, render_steps=10, export_steps=10):

  from fn import Fn
  from time import time
  # from iutils.ioOBJ import export_2d as export

  t0 = time()

  fn = Fn(prefix='./res/')

  def wrap(render):

    dl.step()
    dl.spawn_curl(limit=limit, prob=prob)
    # dl.spawn_normal(limit=limit, prob=prob)

    if dl.itt % render_steps == 0:

      print('itt', dl.itt, 'num', dl.num, 'time', time()-t0)

      num = dl.num

      render.clear_canvas()
      render.set_line_width(2*dl.one)

      xy = dl.xy[:num,:]
      links = dl.links[:num,:]
      # line = dl.get_line()

      render.ctx.set_source_rgba(*colors['front'])

      ## dots
      # for x,y in xy:
        # render.circle(x, y, dl.one, fill=True)

      ## edges
      for i in range(num):
        b = links[i,1]
        render.line(xy[i,0], xy[i,1], xy[b,0], xy[b,1])

      ## connected edges
      # remapped = xy[line,:]
      # render.ctx.move_to(remapped[0,0], remapped[0,1])
      # for x in remapped[:,:]:
      #   render.ctx.line_to(x[0], x[1])
      # render.ctx.fill()

    if dl.itt % export_steps == 0:

      name = fn.name()
      render.write_to_png(name+'.png')
      # export('differential-line-cuda', name+'.2obj', xy, lines=[line])

    return True

  return wrap



def main():

  from modules.differentialLine import DifferentialLine
  from iutils.render import Animate

  colors = {
      'back': [1,1,1,1],
      'front': [0,0,0,0.6],
      'cyan': [0,0.6,0.6,0.6],
      'light': [0,0,0,0.2],
      }

  threads = 512

  render_steps = 10
  export_steps = 14

  size = 512
  one = 1.0/size

  init_num = 20
  init_rad = 0.001

  stp = one*0.4
  spring_stp = 1.0
  reject_stp = 13.0

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

