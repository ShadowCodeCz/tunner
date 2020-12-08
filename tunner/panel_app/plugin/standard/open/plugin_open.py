import os
import datetime
import subprocess
import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.open"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"

    add_plugin_to_panel = "add.plugin.to.panel"
    open_evidence_directory = "open.evidence.directory"


    end_test = "end.test"
    run_test = "run.test"

    unsubscribed_message = "unsubscribed.message"


class TunnerSubscriber(gdp.event.AdvancedSubscriber):
    subscription_messages = []

    def __init__(self, tunner):
        super().__init__(tunner.provider)
        self.tunner = tunner
        for message in self.subscription_messages:
            self.subscribe(message)

    @property
    def gcfg(self):
        return self.tunner.gui.cfg[name]


class GuiConfigurationLoader(TunnerSubscriber):
    subscription_messages = [Message.load_plugin_gui_configuration]

    def update(self, notification):
        self.tunner.gui.cfg[name] = self.tunner.auto_configuration.load_gui_cfg(__file__)


class EvidenceDirectoryOpener(TunnerSubscriber):
    subscription_messages = [Message.open_evidence_directory]

    def update(self, notification):
        subprocess.Popen(r'explorer /select,"%s"' % self.tunner.data["test.run.diectory"])


class OpenPanelButtonEnabler(TunnerSubscriber):
    subscription_messages = [Message.run_test]

    def update(self, notification):
        self.tunner.data["_open.button.state"] = tk.NORMAL
        self.tunner.gui.items[name]["button"]["state"] = tk.NORMAL
        self.tunner.gui.items[name]["button"].bind("<Button-1>", self.tunner.handler.build(Message.open_evidence_directory))


class OpenPanelButtonDisabler(TunnerSubscriber):
    subscription_messages = [Message.end_test]

    def update(self, notification):
        self.tunner.data["_open.button.state"] = tk.DISABLED
        self.tunner.gui.items[name]["button"]["state"] = tk.DISABLED
        self.tunner.gui.items[name]["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))


class PanelAdder(TunnerSubscriber):
    subscription_messages = [Message.add_plugin_to_panel]

    def update(self, notification):
        gui = {}

        self.add_frame(gui)
        self.add_button(gui)

        self.tunner.gui.items[name] = gui

    def add_frame(self, gui):
        gui["frame"] = tk.Frame(self.tunner.gui.panel["frame"])
        gui["frame"].configure(**self.gcfg["plugin"]["frame"]["configure"])
        gui["frame"].grid(**self.gcfg["plugin"]["frame"]["grid"])

    def add_button(self, gui):
        gui["button"] = tk.Button(gui["frame"])
        gui["button"].configure(**self.gcfg["plugin"]["button"]["configure"])
        gui["button"]["state"] = self.tunner.data["_open.button.state"]
        gui["button"].grid(**self.gcfg["plugin"]["button"]["grid"])

        if self.tunner.data["_open.button.state"] == tk.NORMAL:
            gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.open_evidence_directory))
        else:
            gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))


class OpenPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PanelAdder,
            EvidenceDirectoryOpener,
            OpenPanelButtonDisabler,
            OpenPanelButtonEnabler
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))

        self.tunner.data["_open.button.state"] = tk.DISABLED