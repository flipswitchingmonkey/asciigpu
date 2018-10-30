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
    return ""


class Gpu:
    index = 0
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

    def getThrottling(self):
        violationtime = getGpuData(self.index, "power_violation_report")
        return "yes" if violationtime > 0.0 else "no"

    def name(self):
        return getGpuData(self.index, "type")

    def get_type(self):
        return self.type.decode('UTF-8')
    def get_graphics_clock_report(self):
        return self.graphics_clock_report
    def get_sm_clock_report(self):
        return self.sm_clock_report
    def get_mem_clock_report(self):
        return self.mem_clock_report
    def get_uuid(self):
        return self.uuid.decode('UTF-8')
    def get_pci_id(self):
        return self.pci_id
    def get_temp(self):
        return self.temp
    def get_mem_total(self):
        return self.mem_total
    def get_fb_memory(self):
        return self.fb_memory
    def get_ecc_mode(self):
        return self.ecc_mode
    def get_util(self):
        return self.util
    def get_mem_util(self):
        return self.mem_util
    def get_fan(self):
        return self.fan
    def get_power_usage_report(self):
        return self.power_usage_report
    def get_max_graphics_clock(self):
        return self.max_graphics_clock
    def get_max_sm_clock(self):
        return self.max_sm_clock
    def get_max_mem_clock(self):
        return self.max_mem_clock
    def get_power_man_limit(self):
        return self.power_man_limit
    def get_power_violation_report(self):
        return self.power_violation_report
    def get_bar1_memory(self):
        return self.bar1_memory
    def get_bar1_max_memory(self):
        return self.bar1_max_memory
    def get_shutdown_temp(self):
        return self.shutdown_temp
    def get_slowdown_temp(self):
        return self.slowdown_temp
    def get_encoder_util(self):
        return self.encoder_util
    def get_decoder_util(self):
        return self.decoder_util

    def get_mem_used(self):
        return "{0:.2f} MB ({1} %)".format(float(self.get_mem_total()) * float(self.get_mem_util()) / 100.0, self.get_mem_util())

    def collectInfo(self):
        self.type = getGpuData(self.index, "type")
        self.graphics_clock_report = getGpuData(self.index, "graphics_clock_report")
        self.sm_clock_report = getGpuData(self.index, "sm_clock_report")
        self.mem_clock_report = getGpuData(self.index, "mem_clock_report")
        self.uuid = getGpuData(self.index, "uuid")
        self.pci_id = getGpuData(self.index, "pci_id")
        self.temp = getGpuData(self.index, "temp")
        self.mem_total = getGpuData(self.index, "mem_total")
        self.fb_memory = getGpuData(self.index, "fb_memory")
        self.ecc_mode = getGpuData(self.index, "ecc_mode")
        self.util = getGpuData(self.index, "util")
        self.mem_util = getGpuData(self.index, "mem_util")
        self.fan = getGpuData(self.index, "fan")
        self.power_usage_report = getGpuData(self.index, "power_usage_report")
        self.max_graphics_clock = getGpuData(self.index, "max_graphics_clock")
        self.max_sm_clock = getGpuData(self.index, "max_sm_clock")
        self.max_mem_clock = getGpuData(self.index, "max_mem_clock")
        self.power_man_limit = getGpuData(self.index, "power_man_limit")
        self.power_violation_report = getGpuData(self.index, "power_violation_report")
        self.bar1_memory = getGpuData(self.index, "bar1_memory")
        self.bar1_max_memory = getGpuData(self.index, "bar1_max_memory")
        self.shutdown_temp = getGpuData(self.index, "shutdown_temp")
        self.slowdown_temp = getGpuData(self.index, "slowdown_temp")
        self.encoder_util = getGpuData(self.index, "encoder_util")
        self.decoder_util = getGpuData(self.index, "decoder_util")

    def getDetailsAsTuples(self):
        self.collectInfo()
        details = []
        i = 0
        details.append((["Name", "{0}".format(self.get_type())], i))
        i+=1
        details.append((["Utilization (GPU)", "{0} %".format(self.get_util())], i))
        i+=1
        details.append((["Utilization (Encoder)", "{0} %".format(self.get_encoder_util())], i))
        i+=1
        details.append((["Utilization (Decoder)", "{0} %".format(self.get_decoder_util())], i))
        i+=1
        details.append((["Temperature", "{0} C".format(self.get_temp())], i))
        i+=1
        details.append((["Temperature (Shutdown)", "{0} C".format(self.get_shutdown_temp())], i))
        i+=1
        details.append((["Temperature (Slowdown)", "{0} C".format(self.get_slowdown_temp())], i))
        i+=1
        details.append((["GPU Clock Speed", "{0} MHz".format(self.get_graphics_clock_report())], i))
        i+=1
        details.append((["GPU Clock Speed (Max)", "{0} MHz".format(self.get_max_graphics_clock())], i))
        i+=1
        details.append((["Memory Clock Speed", "{0} MHz".format(self.get_mem_clock_report())], i))
        i+=1
        details.append((["Memory Clock Speed (Max)", "{0} MHz".format(self.get_max_mem_clock())], i))
        i+=1
        details.append((["Memory (used)", "{0}".format(self.get_mem_used())], i))
        i+=1
        details.append((["Memory (total)", "{0} MB".format(self.get_mem_total())], i))
        i+=1
        details.append((["UUID", "{0}".format(self.get_uuid())], i))
        i+=1
        details.append((["Fan Speed", "{0} %".format(self.get_fan())], i))
        i+=1
        details.append((["Power Usage", "{0} Watts".format(self.get_power_usage_report())], i))
        i+=1
        details.append((["Power Limit", "{0} Watts".format(self.get_power_man_limit())], i))
        i+=1
        details.append((["Power Violation Report", "{0}".format(self.get_power_violation_report())], i))
        return details


class GpuInfoModel(object):
    _gpus = []

    def __init__(self):
        try:
            print("Initialising nvml...")
            nvmlInit()
            print("Driver Version:", nvmlSystemGetDriverVersion().decode("UTF-8"))
            print("Number of GPUs:", nvidia.get_gpu_num())
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
        ret = [([x.toString(), x.getUsageAsBar(), str(x.getUsage()), str(x.getTemperature()), str(x.getThrottling())], x.index) for x in self._gpus]
        return ret
    
    def get_detail(self, index):
        if len(self._gpus) > index:
            gpu = self._gpus[index]
        else:
            return [(["Name", "Could not find card information"], 0)]
        return gpu.getDetailsAsTuples()

        

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
            columns=[23,53,10,10,14],
            options=model.get_columns(),
            titles=["GPU", "Usage", "Usage", "Temp", "Throttling"],
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
_version = 0.12
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
