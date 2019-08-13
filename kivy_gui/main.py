"""Learning to use Kivy GUI framework."""

from kivy.app import App
from kivy.uix.widget import Widget


class DataWindow(Widget):
    """Root element of Application UI."""

    pass


class DataWindowApp(App):
    def build(self):
        return DataWindow()


if __name__ == "__main__":
    DataWindowApp().run()
