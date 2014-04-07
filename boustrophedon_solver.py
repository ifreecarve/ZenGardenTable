
import math

pythag = math.hypot #lambda x, y: math.sqrt(math.pow(x, 2) + math.pow(y, 2))
pythag2 = lambda x1, y1, x2, y2: pythag(x1 - x2, y1 - y2)
DEBUG = False

class DisplacementError(Exception):
   pass

class BoustrophedonSolver(object):

   def __init__(self, rockpoint_array, canvas, ball_radius):
      self.rockpoint = rockpoint_array
      self.canvas = canvas
      self.radius = ball_radius
      self.ball_coverage_template = self.get_ball_coverage_template(self.radius)
      self.ball_shell_template = self.get_ball_shell_template(self.ball_coverage_template)

   def solve(self):

      covered = [[False for y in col] for col in self.rockpoint]

      for x, row in enumerate(self.rockpoint):
         print "testing col", x
         if x < (self.radius - 1): continue
         if x > (len(self.rockpoint) - self.radius): continue
         for y, is_rock in enumerate(row):
            #print "testing ", x, y
            # test coverage and verify no displacement
            coverage = self.ball_coverage(x, y)
            if DEBUG: print "ball coverage is", coverage
            try:
               d = self.displacement(x, y) #, coverage)
               if (0, 0) == d:
                  # all points ok
                  for xc, yc in coverage:
                     covered[xc][yc] = True
            except DisplacementError:
               pass
            except IndexError:
               print "failed", xc, yc
               raise
            except:
               raise

      print "Drawing cols",
      for x, row in enumerate(self.rockpoint):
         print ".",
         for y, is_rock in enumerate(row):
            if covered[x][y]:

               self.draw_point(x, y, "yellow")

      print


   def get_ball_coverage_template(self, radius):
       """
       get a list of (x, y) points covered by a ball with self.radius

       """

       rr = radius - 1

       out = []
       for x in range(0 - rr, rr + 1):
           for y in range(0 - rr, rr + 1):
               if rr >= pythag(x, y):
                   out.append((x,y))
       return out


   def get_ball_shell_template(self, template):
       """
       get a list of (x, y) points that touch non-ball neighbors

       """

       return [(x, y) for (x, y) in template
               if not all(map(template.__contains__,
                              [(x + 1, y),
                               (x - 1, y),
                               (x, y + 1),
                               (x, y - 1)]))]


   def ball_coverage(self, ctr_x, ctr_y, radius=None):
       """
       get a list of (x, y) points covered by a ball at given center (ctr_x, ctr_y)

       points that overlap the edges are considered
       """

       if radius is not None:
           template = self.get_ball_coverage_template(radius)
       else:
           template = self.ball_coverage_template

       return [(x + ctr_x, y + ctr_y) for (x, y) in template]



   def ball_shell(self, ctr_x, ctr_y, template=None):
       """
       get a list of (x, y) points covered by the shell of a ball at given center
       """
       if template is not None:
           tp = template
       else:
           tp = self.ball_shell_template

       return [(x + ctr_x, y + ctr_y) for (x, y) in template]



   def is_rockpoint(self, x, y):
       if 0 > x or 0 > y: return True
       if x >= len(self.rockpoint): return True

       col = self.rockpoint[x]
       if y >= len(col): return True
       return col[y]


   def displacement(self, ctr_x, ctr_y, coverage=None):
       """
       calculate the displacement of the ball from its desired center

       for every rock point, draw a radius around them of un-allowable area
       of the remaining points, the one closest to the original center is the displacement
       """

       # find coverage of ball
       if None is coverage:
           coverage = self.ball_coverage(ctr_x, ctr_y)

       # find any rock points within the ball
       rockpoints = []
       for (x, y) in coverage:
           if self.is_rockpoint(x, y):
               rockpoints.append((x, y))

       # early exit if no rocks
       if 0 == len(rockpoints):
           return 0, 0

       if DEBUG: print "rockpoints are", rockpoints

       # find the coverage of the rock points, subtract from initial coverage
       uncoverage = set([])
       for (x, y) in rockpoints:
           for (rx, ry) in self.ball_coverage(x, y):
               uncoverage.add((rx, ry))

       # get the squares where coverage is allowed + their distance from ctr
       allowed_coverage = []
       for (x, y) in coverage:
           if not (x, y) in uncoverage:
               allowed_coverage.append((x, y, pythag2(ctr_x, ctr_y, x, y)))

       # minimum displacement from center
       # favor the lower x, y
       def my_min(ac1, ac2):
           if ac1 is None:
               return ac2
           elif ac2 is None:
               return ac1

           x1, y1, d1 = ac1
           x2, y2, d2 = ac2

           if d1 > d2:
               return ac2
           elif d1 < d2:
               return ac1
           else:
               if x1 == x2:
                   if y1 < y2:
                       return ac1
                   else:
                       return ac2
               elif x1 > x2:
                   return ac2
               else:
                   return ac1

       # find what remaining point is the minimum distance from the center
       # start with a bogus point
       min_distance_point = None
       for pt in allowed_coverage:
           min_distance_point = my_min(min_distance_point, pt)

       if min_distance_point is None:
           raise DisplacementError("No allowed coverage for %d, %d" % (ctr_x, ctr_y))

       xm, ym, _ = min_distance_point
       return xm - ctr_x, ym - ctr_y


   def draw_point(self, x, y, color="black"):
       self.canvas.create_line(x, y, x+1, y, smooth=False, fill=color)


   def animate(self):
      self.animation_steps = 100
      self.draw_frame()
      print "Animate is done"


   def draw_frame(self):
      if 0 >= self.animation_steps:
         print "DONE"
      else:
         p  = self.animation_steps
         np = p - 1

         self.canvas.create_line(p, p, np, np, smooth=False, fill="blue")
         self.animation_steps = np

         #self.update_idletasks()

         self.canvas.after(100, self.draw_frame)
