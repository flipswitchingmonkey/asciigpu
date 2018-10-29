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
        return ret
    
    def get_detail(self, index):
        details = []
        i = 0
        details.append((["Name", "{0}".format(getGpuData(index, "type").decode('UTF-8'))], i))
        i+=1
        details.append((["Utilization (GPU)", "{0} %".format(getGpuData(index, "util"))], i))
        i+=1
        details.append((["Utilization (MEM)", "{0} %".format(getGpuData(index, "mem_util"))], i))
        i+=1
        details.append((["GPU Clock Speed", "{0} MHz".format(getGpuData(index, "graphics_clock_report"))], i))
        i+=1
        details.append((["Memory Clock Speed", "{0} MHz".format(getGpuData(index, "mem_clock_report"))], i))
        i+=1
        details.append((["Temperature", "{0} C".format(getGpuData(index, "temp"))], i))
        i+=1
        details.append((["UUID", "{0}".format(getGpuData(index, "uuid").decode('UTF-8'))], i))
        i+=1
        details.append((["Memory (total)", "{0} MB".format(getGpuData(index, "mem_total"))], i))
        i+=1
        return details

class MainView(Frame):
    _currentPick = 0

    def __init__(self, screen, model):
        global _detailIsOpen
        _detailIsOpen == False
        super(MainView, self).__init__(screen,
                                    int(screen.height * 0.9),
                                    int(screen.width * 0.9),
                                    on_load=self._reload_list,
                                    hover_focus=True,
                                    can_scroll=False,
                                    title="asciiGPU {0} (Michael Auerswald @ 908video GmbH)".format(_version))
        # Save off the model that accesses the contacts database.
        self._model = model
        self._refresh = _refreshRate

        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)

        # Create the form for displaying the list of contacts.
        self._list_view = MultiColumnListBox(
            height=Widget.FILL_FRAME,
            columns=[25,55,10,10],
            options=model.get_columns(),
            titles=["GPU", "Usage", "Usage", "Temp"],
            on_change=self._on_pick,
            on_select=self._on_select)
        layout.add_widget(self._list_view)
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        self._refresh_label = Label("Refresh(s): {0:.2f}".format(_refreshRate))
        layout2.add_widget(Button("Quit", self._quit), 0)
        layout2.add_widget(self._refresh_label, 1)
        # layout2.add_widget(Button("-", self._refresh_minus), 2)
        # layout2.add_widget(Button("+", self._refresh_plus), 3)
        layout3 = Layout([1])
        self.add_layout(layout3)
        layout3.add_widget(Label("Press 'q' or 'Esc' to exit. '+'/'-' to change refresh rate.", align="^"), 0)

        self.fix()
        self._on_pick()

    # def _refresh_minus(self):
    #     self._refresh = max(0.1,self._refresh-0.1)
    #     self._refresh_label.text = "Refresh(s): {0:.2f}".format(self._refresh)
    #     self._reload_list()
    
    # def _refresh_plus(self):
    #     self._refresh = max(0.1,self._refresh+0.1)
    #     self._refresh_label.text = "Refresh(s): {0:.2f}".format(self._refresh)
    #     self._reload_list()

    def _on_pick(self):
        self._currentPick = self._list_view.value

    def _on_select(self):
        global _currentIndex, _detailIsOpen
        _detailIsOpen = True
        _currentIndex = self._currentPick
        raise NextScene("Detail")

    def _reload_list(self, new_value=None):
        global _updateThread
        temp = self._currentPick
        self._list_view.options = self._model.get_columns()
        self._list_view.value = temp
        self._refresh_label.text = "Refresh(s): {0:.2f}".format(_refreshRate)
        _screen.force_update()
        if _updateThread and _updateThread.is_alive:
            _updateThread.cancel()
        _updateThread = Timer(_refreshRate, self._reload_list)
        _updateThread.start()

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")


class DetailView(Frame):
    def __init__(self, screen, model):
        global _detailIsOpen, _currentIndex
        _detailIsOpen = True
        super(DetailView, self).__init__(screen,
                                    int(screen.height * 0.8),
                                    int(screen.width * 0.8),
                                    on_load=self._reload_list,
                                    hover_focus=True,
                                    can_scroll=False,
                                    title="Detail View")
        # Save off the model that accesses the contacts database.
        self._model = model
        self._refresh = _refreshRate

        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)

        self._list_detail_view = MultiColumnListBox(
            height=Widget.FILL_FRAME,
            columns=["<50%","<50%"],
            options=model.get_detail(_currentIndex),
            titles=["Parameter", "Value"],
            on_change=self._on_pick)
        layout.add_widget(self._list_detail_view)
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        self._refresh_label = Label("Refresh(s): {0:.2f}".format(_refreshRate))
        layout2.add_widget(Button("close", self._cancel), 0)
        layout2.add_widget(self._refresh_label, 1)
        layout3 = Layout([1])
        self.add_layout(layout3)
        layout3.add_widget(Label("Press 'Esc' to close. '+'/'-' to change refresh rate.", align="^"), 0)

    # def _refresh_minus(self):
    #     self._refresh = max(0.1,self._refresh-0.1)
    #     self._refresh_label.text = "Refresh(s): {0:.2f}".format(self._refresh)
    #     self._reload_list()
    
    # def _refresh_plus(self):
    #     self._refresh = max(0.1,self._refresh+0.1)
    #     self._refresh_label.text = "Refresh(s): {0:.2f}".format(self._refresh)
    #     self._reload_list()

        self.fix()
        self._on_pick()

    def _on_pick(self):
        self._currentPick = self._list_detail_view.value

    # def _on_select(self):
    #     global _currentIndex
    #     _currentIndex = self._currentPick
    #     raise NextScene("Detail")

    def _reload_list(self, new_value=None):
        global _updateThread, _currentIndex
        temp = self._currentPick
        self._list_detail_view.options = self._model.get_detail(_currentIndex)
        self._list_detail_view.value = temp
        _screen.force_update()

        if _updateThread and _updateThread.is_alive:
            _updateThread.cancel()
        _updateThread = Timer(_refreshRate, self._reload_list)
        _updateThread.start()

    @staticmethod
    def _cancel():
        global _detailIsOpen
        _detailIsOpen = False
        raise NextScene("Main")

def shutdown():
    global _updateThread
    print("Stopping update thread...")
    _updateThread.cancel()
    print("Shutting down nvml...")
    nvmlShutdown()
    print("Exiting ...")
    sys.exit(0)

def global_shortcuts(event):
    global _mainView, _detailIsOpen, _refreshRate
    if isinstance(event, KeyboardEvent):
        c = event.key_code
        # print(c)
        # Stop on ctrl+q or ctrl+x
        if c == 45:
            _refreshRate = max(0.1, _refreshRate-0.1)
            if _detailIsOpen == False:
                # _mainView._refresh_minus()
                _mainView._refresh_label.text = "Refresh(s): {0:.2f}".format(_refreshRate)
            else:
                # _detailView._refresh_minus()
                _detailView._refresh_label.text = "Refresh(s): {0:.2f}".format(_refreshRate)
        elif c == 43:
            _refreshRate = max(0.1, _refreshRate+0.1)
            if _detailIsOpen == False:
            #     _mainView._refresh_plus()
                _mainView._refresh_label.text = "Refresh(s): {0:.2f}".format(_refreshRate)
            else:
            #     _detailView._refresh_minus()
                _detailView._refresh_label.text = "Refresh(s): {0:.2f}".format(_refreshRate)

        elif c == 113 or c == -1:
            if _detailIsOpen == False:
                raise StopApplication("User terminated app")
            else:
                _detailIsOpen = False
                raise NextScene("Main")
        elif c in (17, 24):
            raise StopApplication("User terminated app")

def main(screen, scene):
    global _mainView, _detailView, _screen, _detailIsOpen
    _screen = screen
    _mainView = MainView(screen, _gpuinfo)
    _detailView = DetailView(screen, _gpuinfo)
    _detailIsOpen = False
    scenes = [
        Scene([_mainView], -1, name="Main"),
        Scene([_detailView], -1, name="Detail")
    ]
    # scenes = [
    #     Scene([ListView(screen, contacts)], -1, name="Main"),
    #     Scene([ContactView(screen, contacts)], -1, name="Edit Contact")
    # ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene, unhandled_input=global_shortcuts)



last_scene = None
_version = 0.11
_refreshRate = 0.5
_Gpus = []
_screen = None
_updateThread = None
_gpuinfo = GpuInfoModel()
_mainView = None
_detailView = None
_currentIndex = 0
_detailIsOpen = False
while True:
    try:
        # init()
        Screen.wrapper(main, catch_interrupt=True, arguments=[last_scene])
        shutdown()
    except ResizeScreenError as e:
        last_scene = e.scene
