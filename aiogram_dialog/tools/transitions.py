import os.path
from typing import List, Sequence, Tuple, Union

from aiogram.dispatcher.fsm.state import State
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom

from aiogram_dialog import Dialog, DialogRegistry
from aiogram_dialog.widgets.kbd import Group, Back, Cancel, Start, SwitchTo, Next

ICON_PATH = os.path.join(os.path.dirname(__file__), "calculator.png")


def widget_edges(nodes, dialog, starts, current_state, kbd):
    if isinstance(kbd, Start):
        nodes[current_state] >> Edge(color="#338a3e") >> nodes[kbd.state]
    elif isinstance(kbd, SwitchTo):
        nodes[current_state] >> Edge(color="#0086c3") >> nodes[kbd.state]
    elif isinstance(kbd, Next):
        new_state = dialog.states[dialog.states.index(current_state) + 1]
        nodes[current_state] >> Edge(color="#0086c3") >> nodes[new_state]
    elif isinstance(kbd, Back):
        new_state = dialog.states[dialog.states.index(current_state) - 1]
        nodes[current_state] >> Edge(color="grey") >> nodes[new_state]
    elif isinstance(kbd, Cancel):
        for from_, to_ in starts:
            if to_.group == current_state.group:
                nodes[current_state] >> Edge(color="grey", style="dashed") >> nodes[from_]


def walk_keyboard(nodes, dialog, starts: List[Tuple[State, State]], current_state: State,
                  keyboards: Sequence):
    for kbd in keyboards:
        if isinstance(kbd, Group):
            walk_keyboard(nodes, dialog, starts, current_state, kbd.buttons)
        else:
            widget_edges(nodes, dialog, starts, current_state, kbd)


def find_starts(current_state, keyboards: Sequence):
    for kbd in keyboards:
        if isinstance(kbd, Group):
            yield from find_starts(current_state, kbd.buttons)
        elif isinstance(kbd, Start):
            yield current_state, kbd.state


def render_transitions(dialogs: Union[List[Dialog], DialogRegistry],
                       title: str = "Aiogram Dialog",
                       filename: str = "aiogram_dialog",
                       format: str = "png"):
    if isinstance(dialogs, DialogRegistry):
        dialogs = list(dialogs.dialogs.values())

    with Diagram(title, filename=filename, outformat=format, show=False):
        nodes = {}
        for dialog in dialogs:
            with Cluster(dialog.states_group_name()):
                for window in dialog.windows.values():
                    nodes[window.get_state()] = Custom(icon_path=ICON_PATH,
                                                       label=window.get_state().state)

        starts = []
        for dialog in dialogs:
            for window in dialog.windows.values():
                starts.extend(find_starts(window.get_state(), [window.keyboard]))

        for dialog in dialogs:
            for window in dialog.windows.values():
                walk_keyboard(nodes, dialog, starts, window.get_state(), [window.keyboard])
                preview_add_transitions = getattr(window, "preview_add_transitions", None)
                if preview_add_transitions:
                    walk_keyboard(nodes, dialog, starts, window.get_state(),
                                  preview_add_transitions)
