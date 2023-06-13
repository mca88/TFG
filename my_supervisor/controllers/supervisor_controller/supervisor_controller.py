from controller import Supervisor
from random import randint

TIME_STEP = 100

robot = Supervisor()  # create Supervisor instance

# [CODE PLACEHOLDER 1]

bb8 = robot.getFromDef('BB-8')
tf = bb8.getField('translation')

i = 0
while robot.step(TIME_STEP) != -1:
  # [CODE PLACEHOLDER 2]
  x = randint(-5,5)
  y = randint(-5,5)
  
  if i == 1:
      new_value = [x, y, 0]
      tf.setSFVec3f(new_value)
  i += 1