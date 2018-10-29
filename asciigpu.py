from random import randint
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, MultiColumnListBox, Widget, Label, _split_text
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from pynvml import *
import nvidia
from threading import Timer, Thread, Event

def getGpuData(index, name):
    try:
        return nvidia.gpu_device_handler("gpu{0}_{1}".format(index, name))
    except NVMLError as nverr:
        print("NVMLError " + str(nverr))
    except Exception as err:
        print("Exception " + str(err))


class Gpu:
    index = 0
    handle = None
    def __init__(self, index=0):
        self.index = index
    
    def toString(self):
        try:
            return "{0}:{1}".format(self.index, self.name().decode('UTF-8'))
        except:
            return "Error"

    def getFan(self):
        return getGpuData(self.index, "fan")

    def getUsage(self):
        return getGpuData(self.index, "util")

    def getUsageAsBar(self, minval=0, maxVal=100):
        try:
            usage = getGpuData(self.index, "util")
            cube = "■"
            bar = ""
            for i in range(round(usage/2.0)):
                bar += cube
            return bar
        except:
            return "Error"

    def getTemperature(self):
        return getGpuData(self.index, "temp")
    
    def name(self):
        return getGpuData(self.index, "type")

class GpuInfoModel(object):
    _gpus = []

    def __init__(self):
        try:
            print("Initialising nvml...")
            nvmlInit()
            print("Driver Version:", nvmlSystemGetDriverVersion())
            print(nvidia.get_gpu_num())
            for i in range(nvidia.get_gpu_num()):
                self.addGpu(i)
        except NVMLError as err:
            print("Failed to initialize NVML: ", err)
            print("Exiting...")
            os._exit(1)
    
    def addGpu(self, index):
        self._gpus.append(Gpu(index))

    def get_summary(self):
        return [(x.toString(), x.index) for x in self._gpus]

    def get_columns(self):
        ret = [([x.toString(), x.getUsageAsBar(), str(x.getUsage()), str(x.getTemperature())], x.index) for x in self._gpus]
        # print(ret)
        return ret

class ProgressBar(Label):
    _progress = 0

    def __init__(self, value, width=100, minval=0, maxval=100, height=1, align="<"):
        """
        :param label: The text to be displayed for the Label.
        :param height: Optional height for the label.  Defaults to 1 line.
        :param align: Optional alignment for the Label.  Defaults to left aligned.
            Options are "<" = left, ">" = right and "^" = centre
        """
        # Labels have no value and so should have no name for look-ups either.
        super(Label, self).__init__(None, tab_stop=False)
        # Although this is a label, we don't want it to contribute to the layout
        # tab calculations, so leave internal `_label` value as None.
        self._progress = value
        self._minval = minval
        self._maxval = maxval
        self._width = width
        self._required_height = height
        self._align = align
        self._text = "***"

    def update(self, frame_no):
        (colour, attr, bg) = self._frame.palette["label"]
        self._text = ""
        for i in range(self._progress):
            self._text += "■"
        for i, text in enumerate(_split_text(self._text, self._w, self._h, self._frame.canvas.unicode_aware)):
            self._frame.canvas.paint(
                "{:{}{}}".format(self._text, self._align, self._w), self._x, self._y + i, colour, attr, bg)

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, new_value):
        self._progress = new_value

class MainView(Frame):
    def __init__(self, screen, model):
        super(MainView, self).__init__(screen,
                                    int(screen.height * 0.9),
                                    int(screen.width * 0.9),
                                    on_load=self._reload_list,
                                    hover_focus=True,
                                    can_scroll=False,
                                    title="GPU List")
        # Save off the model that accesses the contacts database.
        self._model = model
        self._refresh = _defaultRefresh

        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)

        # Create the form for displaying the list of contacts.
        self._list_view = MultiColumnListBox(
            height=Widget.FILL_FRAME,
            columns=[25,55,10,10],
            options=model.get_columns(),
            titles=["GPU", "Usage", "Usage", "Temp"],
            on_change=self._on_pick)
        layout.add_widget(self._list_view)
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        self._refresh_label = Label("Refresh(s): {0:.2f}".format(self._refresh))
        layout2.add_widget(Button("Quit", self._quit), 0)
        layout2.add_widget(self._refresh_label, 1)
        layout2.add_widget(Button("-", self._refresh_minus), 2)
        layout2.add_widget(Button("+", self._refresh_plus), 3)

        # self.startTimer()

        self.fix()
        self._on_pick()

    def _refresh_minus(self):
        self._refresh = max(0.1,self._refresh-0.1)
        self._refresh_label.text = "Refresh(s): {0:.2f}".format(self._refresh)
        self._reload_list()
    
    def _refresh_plus(self):
        self._refresh = max(0.1,self._refresh+0.1)
        self._refresh_label.text = "Refresh(s): {0:.2f}".format(self._refresh)
        self._reload_list()

    def _on_pick(self):
        pass
    #     self._edit_button.disabled = self._list_view.value is None
    #     self._delete_button.disabled = self._list_view.value is None

    def _reload_list(self, new_value=None):
        # print("reloading")
        global _updateThread
        self._list_view.options = self._model.get_columns()
        self._list_view.value = new_value
        _screen.force_update()
        if _updateThread and _updateThread.is_alive:
            _updateThread.cancel()
        _updateThread = Timer(self._refresh, self._reload_list)
        _updateThread.start()

    # def _add(self):
        # pass
    #     self._model.current_id = None
    #     raise NextScene("Edit Contact")

    # def _edit(self):
        # pass
    #     self.save()
    #     self._model.current_id = self.data["contacts"]
    #     raise NextScene("Edit Contact")

    #def _delete(self):
    #     pass
    #     self.save()
    #     self._model.delete_contact(self.data["contacts"])
    #     self._reload_list()

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")


def shutdown():
    global _updateThread
    print("Stopping update thread...")
    _updateThread.cancel()
    print("Shutting down nvml...")
    nvmlShutdown()
    print("Exiting ...")
    sys.exit(0)

def global_shortcuts(event):
    if isinstance(event, KeyboardEvent):
        c = event.key_code
        # print(c)
        # Stop on ctrl+q or ctrl+x
        if c == 113 or c == -1:
            raise StopApplication("User terminated app")
        if c in (17, 24):
            raise StopApplication("User terminated app")

def main(screen, scene):
    global _mainView, _screen
    _screen = screen
    mainview = MainView(screen, _gpuinfo)
    scenes = [
        Scene([mainview], -1, name="Main")
    ]
    # scenes = [
    #     Scene([ListView(screen, contacts)], -1, name="Main"),
    #     Scene([ContactView(screen, contacts)], -1, name="Edit Contact")
    # ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene, unhandled_input=global_shortcuts)



last_scene = None
_defaultRefresh = 0.5
_Gpus = []
_screen = None
_updateThread = None
_gpuinfo = GpuInfoModel()
_mainView = None
while True:
    try:
        # init()
        Screen.wrapper(main, catch_interrupt=True, arguments=[last_scene])
        shutdown()
    except ResizeScreenError as e:
        last_scene = e.scene
