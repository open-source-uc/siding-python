from asciimatics.widgets import Frame, TextBox, Layout, Label, Divider, Text, \
    CheckBox, RadioButtons, Button, PopUpDialog
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication, \
    InvalidFields
import sys
import os

form_data = {
  'user': os.environ['USER'] if os.environ.get('USER') else "",
  'passwd': os.environ['PASSWD'] if os.environ.get('USER') else ""
}

class Login(Frame):
  def __init__(self, screen, siding):
    super(Login, self).__init__(screen,
                                    int(screen.height * 2 // 3),
                                    int(screen.width * 2 // 3),
                                    has_shadow=False,
                                    data = form_data,
                                    name="Login")
    self.siding = siding
    layout = Layout([1, 3, 1], fill_frame= True)
    self.add_layout(layout)
    self._reset_button = Button("Reset", self._reset)
    layout.add_widget(Divider(draw_line=False, height=screen.height//4),1)

    layout.add_widget(
            Text(label="Username:",
                 name="user",
                 on_change=self._on_change), 1)

    layout.add_widget(
        Text(label="Password:",
              name="passwd",
              on_change=self._on_change), 1)

    #Set button layout

    layout2 = Layout([1, 1, 1])
    self.add_layout(layout2)
    layout2.add_widget(self._reset_button, 0)
    layout2.add_widget(Button("Login", self._login), 1)
    layout2.add_widget(Button("Quit", self._quit), 2)
    self.fix()

    
  
  def _login(self):
      status = self.siding.login(self.data['user'],self.data['passwd'])
      self._scene.add_effect(
            PopUpDialog(self._screen, status, ["OK"]))
      if self.siding.logged:
        raise NextScene("Cursos")

  def _on_change(self):
      changed = False
      self.save()
      for key, value in self.data.items():
          if key not in form_data or form_data[key] != value:
              changed = True
              break
      self._reset_button.disabled = not changed

  def _reset(self):
      self.reset()
      raise NextScene()

  def _quit(self):
    self._scene.add_effect(
        PopUpDialog(self._screen,
                    "Are you sure?",
                    ["Yes", "No"],
                    on_close=self._quit_on_yes))

  @staticmethod
  def _quit_on_yes(selected):
    # Yes is the first button
    if selected == 0:
      raise StopApplication("User requested exit")


  def process_event(self, event):
      # Do the key handling for this Frame.
      if isinstance(event, KeyboardEvent):
          if event.key_code in [Screen.ctrl("q")]:
              raise StopApplication("User quit")

      # Now pass on to lower levels for normal handling of the event.
      return super(Login, self).process_event(event)

if __name__ == '__main__':


  def demo(screen, scene):
    scenes = [
        Scene([Login(screen)], -1, name="login-form"),
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene)

  last_scene = None
  while True:
      try:
          Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
          sys.exit(0)
      except ResizeScreenError as e:
          last_scene = e.scene