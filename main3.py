from asciimatics.exceptions import (InvalidFields, NextScene,
                                    ResizeScreenError, StopApplication)
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from Siding2 import Siding
from SidingTUI import Login


def demo(screen, scene):
    scenes = [
        Scene([Login(screen, Siding)], -1, name="Login"),
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene)

def main():
 

  last_scene = None
  while True:
      try:
          Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
          sys.exit(0)
      except ResizeScreenError as e:
          last_scene = e.scene

if __name__ == '__main__':
  main()
