from abc import ABC, abstractmethod
from functools import reduce
from enum import Enum, auto
from time import time

from prompt_toolkit import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.filters import renderer_height_is_known, has_focus
from button_replacement import Button
from prompt_toolkit.widgets import (
    Dialog,
    Label,
    TextArea,
    Box,
    Frame,
    RadioList,
    CheckboxList
)
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.containers import (
    Window,
    ConditionalContainer,
    DynamicContainer,
    VSplit,
    HSplit,
    WindowAlign,
    HorizontalAlign,
    VerticalAlign
)
from prompt_toolkit.layout import Layout
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.application.current import get_app
from prompt_toolkit.application import Application


# The target element to focus when switching scenes. if none, equals None.
# this is safe because only one app can run at a time.
global__default_target_focus = None


def exit_current_app():
    """Exits the current application, restoring previous terminal state."""
    get_app().exit()


def focus_first_element():
    """Places focus on the first element on the screen for the current running
    application."""
    app = get_app()

    # Focus first window.
    app.layout.focus(next(app.layout.find_all_windows()))

    # Focus first ui element, eg. button.
    app.layout.focus_next()


tab_bindings = KeyBindings()
tab_bindings.add('tab')(focus_next)
tab_bindings.add('s-tab')(focus_previous)

exit_bindings = KeyBindings()
exit_bindings.add('c-c')(lambda e: exit_current_app())


def InputDialog(
    on_ok,
    on_cancel,
    title,
    prompt,
    ok_text="OK",
    cancel_text="Cancel",
    is_text_valid=lambda text: True
) -> Dialog:
    """Returns a Dialogue component displaying a text input box."""

    def on_accept(buffer):
        if is_text_valid(textfield.text):
            get_app().layout.focus(ok_button)
        return True  # Keeps text.

    def on_ok_clicked():
        if is_text_valid(textfield.text):
            on_ok(textfield.text)

    ok_button = Button(text=ok_text, handler=on_ok_clicked)
    exit_button = Button(text=cancel_text, handler=on_cancel)
    textfield = TextArea(
        multiline=False, accept_handler=on_accept, style='bg:#88ff88 #000000')

    dialog = Dialog(
        title=title,
        body=HSplit(
            [Label(text=prompt, dont_extend_height=True), textfield],
            padding=Dimension(preferred=1, max=1)
        ),
        buttons=[ok_button, exit_button],
        with_background=True
    )

    return dialog


class ToolbarFrameToolbarPosition(Enum):
    TOP = auto()
    BOTTOM = auto()


def ToolbarFrame(body, toolbar_content, position):
    if position == ToolbarFrameToolbarPosition.TOP:
        return HSplit([toolbar_content, Frame(body)])

    toolbar = ConditionalContainer(
        content=toolbar_content,
        filter=renderer_height_is_known
    )

    return HSplit([Frame(body), toolbar])


class RootScreenType(Enum):
    SET_USERNAME = auto()
    MENU = auto()
    SETTINGS = auto()
    HELP = auto()
    PLAYING = auto()


class UsernameScreenState:
    root_screen_type = RootScreenType.SET_USERNAME


class MenuScreenState:
    root_screen_type = RootScreenType.MENU

    def __init__(self, session):
        self.session = session


class HelpScreenState:
    root_screen_type = RootScreenType.HELP

    def __init__(self, session, previous_state):
        self.session = session
        self.previous_state = previous_state


class SettingsScreenState:
    root_screen_type = RootScreenType.SETTINGS

    def __init__(self, session):
        self.session = session


class Session:
    def __init__(self, username, settings):
        self.username = username
        self.settings = settings


class Test:
    def __init__(self, settings):
        self.settings = settings


class TestSettings:
    def __init__(self, difficulty, time_limit, content):
        self.difficulty = difficulty
        self.time_limit = time_limit
        self.content = content


class TestDifficultySetting(Enum):
    EASY = auto()
    NORMAL = auto()
    HARD = auto()
    GOD_MODE = auto()


class TestTimeLimitSetting(Enum):
    """Measured in Seconds"""
    UNLIMITED = -1
    SLOW = 120
    NORMAL = 45
    FAST = 15


class TestContentArea(Enum):
    NUMBER_THEORY = auto()
    ALGEBRA = auto()
    GEOMETRY = auto()


def SetUsernameScreen(controller):
    def is_username_valid(username):
        return len(username) > 0

    def on_username(username):
        session = Session(
            username=username,
            settings=TestSettings(
                difficulty=TestDifficultySetting.NORMAL,
                time_limit=TestTimeLimitSetting.NORMAL,
                content=set((
                    TestContentArea.NUMBER_THEORY,
                    TestContentArea.ALGEBRA,
                    TestContentArea.GEOMETRY
                ))
            )
        )
        new_state = MenuScreenState(session)
        controller.set_state(new_state)

    return InputDialog(
        on_ok=on_username,
        on_cancel=exit_current_app,
        title='Quick Maths',
        prompt=HTML('<i>What is your name?</i>'),
        cancel_text='Quit',
        is_text_valid=is_username_valid
    )


def create_button_list_keybindings(buttons, key_previous, key_next):
    keybindings = KeyBindings()

    if len(buttons) > 1:
        # pylint: disable=invalid-unary-operand-type
        is_first_not_selected = ~has_focus(buttons[0])
        # pylint: disable=invalid-unary-operand-type
        is_last_not_selected = ~has_focus(buttons[-1])

        keybindings.add(key_previous, filter=is_first_not_selected)(
            focus_previous)
        keybindings.add(key_next, filter=is_last_not_selected)(focus_next)

    return keybindings


def create_vertical_button_list_keybindings(buttons):
    return create_button_list_keybindings(buttons, 'up', 'down')


def create_horizontal_button_list_keybindings(buttons):
    return create_button_list_keybindings(buttons, 'left', 'right')


def MenuScreen(controller):
    def on_start_click():
        pass

    def on_settings_click():
        new_state = SettingsScreenState(session=controller.state.session)
        controller.set_state(new_state)

    def on_help_click():
        new_state = HelpScreenState(
            session=controller.state.session,
            previous_state=controller.state
        )
        controller.set_state(new_state)

    buttons = [
        Button('start', handler=on_start_click),
        Button('settings', handler=on_settings_click),
        Button('help', handler=on_help_click),
        Button('quit', handler=exit_current_app)
    ]

    keybindings = create_vertical_button_list_keybindings(buttons)

    body = Box(
        VSplit([
            HSplit(
                children=buttons,
                padding=Dimension(preferred=1, max=1),
                key_bindings=keybindings
            )
        ]),
        style='bg:#000000 #ffffff'
    )

    toolbar_content = Window(
        content=FormattedTextControl(
            "Hello %s. Let's play Quick Maths!" % controller.state.session.username
        ),
        align=WindowAlign.CENTER,
        height=1
    )

    return ToolbarFrame(body=body, toolbar_content=toolbar_content, position=ToolbarFrameToolbarPosition.TOP)


help_text = '''   ____  _    _ _____ _____ _  __  __  __       _______ _    _  _____
  / __ \\| |  | |_   _/ ____| |/ / |  \\/  |   /\\|__   __| |  | |/ ____|
 | |  | | |  | | | || |    | ' /  | \\  / |  /  \\  | |  | |__| | (___
 | |  | | |  | | | || |    |  <   | |\\/| | / /\\ \\ | |  |  __  |\\___ \\
 | |__| | |__| |_| || |____| . \\  | |  | |/ ____ \\| |  | |  | |____) |
  \\___\\_\\\\____/|_____\\_____|_|\\_\\ |_|  |_/_/    \\_\\_|  |_|  |_|_____/


CONTROLS:

Left/Right/Up/Down/Tab/Shift-Tab: Navigate through buttons.

Enter: Click the selected button

Note: You can also click buttons with your mouse

Ctrl-C: Exit'''


def HelpScreen(controller):
    body = Box(
        TextArea(
            help_text,
            focusable=False,
            scrollbar=True
        ),
        padding=0,
        padding_left=1,
        padding_right=1,
        style='bg:#88ff88 #000000'
    )

    def on_back_click():
        new_state = controller.state.previous_state
        controller.set_state(new_state)

    buttons = [
        Button('back', handler=on_back_click),
        Button('quit', handler=exit_current_app)
    ]

    keybindings = create_horizontal_button_list_keybindings(buttons)

    toolbar_content = Box(
        VSplit(
            children=buttons,
            align=HorizontalAlign.CENTER,
            padding=Dimension(preferred=10, max=10),
            key_bindings=keybindings
        ),
        height=1
    )

    return ToolbarFrame(body, toolbar_content, position=ToolbarFrameToolbarPosition.BOTTOM)


def SettingsScreen(controller):
    difficulty_ui = RadioList(values=[
        (TestDifficultySetting.EASY, 'Easy'),
        (TestDifficultySetting.NORMAL, 'Normal'),
        (TestDifficultySetting.HARD, 'Hard'),
        (TestDifficultySetting.GOD_MODE, 'God Mode'),
    ])

    difficulty_ui.current_value = controller.state.session.settings.difficulty

    time_limit_ui = RadioList(values=[
        (TestTimeLimitSetting.UNLIMITED, 'Unlimited'),
        (TestTimeLimitSetting.SLOW, '%ss' %
         TestTimeLimitSetting.SLOW.value),
        (TestTimeLimitSetting.NORMAL, '%ss' %
         TestTimeLimitSetting.NORMAL.value),
        (TestTimeLimitSetting.FAST, '%ss' %
         TestTimeLimitSetting.FAST.value),
    ])

    time_limit_ui.current_value = controller.state.session.settings.time_limit

    content_ui = CheckboxList(values=[
        (TestContentArea.NUMBER_THEORY, 'Number Theory'),
        (TestContentArea.ALGEBRA, 'Algebra'),
        (TestContentArea.GEOMETRY, 'Geometry')
    ])

    content_ui.current_values = list(controller.state.session.settings.content)

    body = Box(
        HSplit(
            [
                Label(
                    text=HTML('<b><i>Settings</i></b>'),
                    dont_extend_height=True,
                ),
                VSplit(
                    [
                        HSplit(
                            [
                                Label(
                                    text=HTML('<b>Difficulty</b>'),
                                    dont_extend_height=True
                                ),
                                difficulty_ui,
                                Label(
                                    text=HTML('<b>Time Limit (Per Q.)</b>'),
                                    dont_extend_height=True
                                ),
                                time_limit_ui
                            ],
                            padding=Dimension(preferred=1, max=1)
                        ),
                        HSplit(
                            [
                                Label(text=HTML('<b>Test Content</b>')),
                                content_ui
                            ],
                            padding=Dimension(preferred=1, max=1)
                        )
                    ],
                )
            ],
            padding=Dimension(preferred=1, max=1)
        ),
        style='bg:#88ff88 #000000'
    )

    def on_back_click():
        difficulty = difficulty_ui.current_value
        time_limit = time_limit_ui.current_value
        content = content_ui.current_values

        if len(content) == 0:
            app = get_app()
            content_ui._selected_index = 0
            app.layout.focus(content_ui)
            return

        new_state = MenuScreenState(
            session=Session(
                username=controller.state.session.username,
                settings=TestSettings(
                    difficulty=difficulty,
                    time_limit=time_limit,
                    content=set(content)
                )
            )
        )
        controller.set_state(new_state)

    buttons = [
        Button('back', handler=on_back_click),
        Button('quit', handler=exit_current_app)
    ]

    toolbar_content = Box(
        VSplit(
            children=buttons,
            align=HorizontalAlign.CENTER,
            padding=Dimension(preferred=10, max=10),
            key_bindings=create_horizontal_button_list_keybindings(buttons)
        ),
        height=1
    )

    return ToolbarFrame(body, toolbar_content, position=ToolbarFrameToolbarPosition.BOTTOM)


def RootScreen(controller):
    state = controller.state

    if state.root_screen_type == RootScreenType.SET_USERNAME:
        return SetUsernameScreen(controller)

    if state.root_screen_type == RootScreenType.MENU:
        return MenuScreen(controller)

    if state.root_screen_type == RootScreenType.HELP:
        return HelpScreen(controller)

    if state.root_screen_type == RootScreenType.SETTINGS:
        return SettingsScreen(controller)


class Controller:
    def __init__(self, state, Screen):
        self._Screen = Screen
        self._container = DynamicContainer(lambda: self._current_screen)
        self.set_state(state)

    def set_state(self, new_state):
        self.state = new_state
        self._current_screen = self._Screen(self)

    def __pt_container__(self):
        return self._container


def RootController(root_state=UsernameScreenState()):
    return Controller(root_state, RootScreen)


root_style = Style.from_dict({
    'dialog': 'bg:#88ff88',
    'dialog frame.label': 'bg:#55aa55 #000000',
    'dialog.body': 'bg:#000000 #00ff00',
    'dialog shadow': 'bg:#00aa00',
    'button.focused': 'bg:#228822'
})


def build_application():
    layout = Layout(RootController())

    def ensure_focus(_):
        """Ensures that at least one element on the screen is focused"""
        app = get_app()

        # When switching screens or something prompt_toolkit doesn't recognize
        # the new focusable elements added to the screen. This will ensure that
        # at least one container/ui is marked as focusable so the screen can be
        # interacted with.

        global global__default_target_focus  # Preferred element to be focused.

        if global__default_target_focus:
            app.layout.focus(global__default_target_focus)
            global__default_target_focus = None  # Reset for next render.

            app.invalidate()  # Trigger re-render.
        elif len(app.layout.get_visible_focusable_windows()) == 0:
            focus_first_element()

            app.invalidate()  # Trigger re-render.

    return Application(
        layout=layout,
        key_bindings=merge_key_bindings([tab_bindings, exit_bindings]),
        full_screen=True,
        mouse_support=True,
        after_render=ensure_focus,
        style=root_style
    )


def main():
    build_application().run()


if __name__ == "__main__":
    main()
