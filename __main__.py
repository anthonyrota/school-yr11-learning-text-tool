from abc import ABC, abstractmethod
from functools import reduce
from enum import Enum, auto
from time import time
from string import ascii_uppercase
from random import randint, choice as random_choice, sample as random_sample

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


class PlayingScreenState:
    root_screen_type = RootScreenType.PLAYING

    def __init__(self, session):
        self.session = session


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
        self.question_number = 0
        self.questions_correct = 0


class TestSettings:
    def __init__(self, difficulty, time_limit, content, question_count):
        self.difficulty = difficulty
        self.time_limit = time_limit
        self.content = content
        self.question_count = question_count


class TestDifficultySetting(Enum):
    NORMAL = auto()
    HARD = auto()


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


class TestQuestionCountSetting(Enum):
    SHORT = 15
    NORMAL = 30
    LONG = 60


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
                    # TestContentArea.ALGEBRA,
                    # TestContentArea.GEOMETRY
                )),
                question_count=TestQuestionCountSetting.NORMAL
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


def MenuScreen(controller):
    def on_start_click():
        new_state = PlayingScreenState(session=controller.state.session)
        controller.set_state(new_state)

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
        (TestDifficultySetting.NORMAL, 'Normal'),
        (TestDifficultySetting.HARD, 'Hard'),
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

    question_count_ui = RadioList(values=[
        (TestQuestionCountSetting.SHORT, str(TestQuestionCountSetting.SHORT.value)),
        (TestQuestionCountSetting.NORMAL, str(
            TestQuestionCountSetting.NORMAL.value)),
        (TestQuestionCountSetting.LONG, str(TestQuestionCountSetting.LONG.value)),
    ])
    question_count_ui.current_value = controller.state.session.settings.question_count

    body_keybindings = KeyBindings()

    @body_keybindings.add('escape')
    def _body_on_key_esc(_):
        app = get_app()
        first_toolbar_button = buttons[0]
        app.layout.focus(first_toolbar_button)

    body = Box(
        HSplit(
            [
                Label(text=HTML('<b><i>Settings</i></b>')),
                VSplit(
                    [
                        HSplit(
                            [
                                Label(text=HTML('<b>Difficulty</b>')),
                                difficulty_ui,
                                Label(text=HTML('<b>Time Limit (Per Q.)</b>')),
                                time_limit_ui
                            ],
                            padding=Dimension(preferred=1, max=1),
                        ),
                        HSplit(
                            [
                                Label(text=HTML('<b>Test Content</b>')),
                                content_ui,
                                Label(text=HTML('<b>Question Count</b>')),
                                question_count_ui
                            ],
                            padding=Dimension(preferred=1, max=1)
                        )
                    ],
                )
            ],
            key_bindings=body_keybindings,
            padding=Dimension(preferred=1, max=1)
        ),
        style='bg:#88ff88 #000000'
    )

    def on_back_click():
        difficulty = difficulty_ui.current_value
        time_limit = time_limit_ui.current_value
        content = content_ui.current_values
        question_count = question_count_ui.current_value

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
                    content=set(content),
                    question_count=question_count
                )
            )
        )
        controller.set_state(new_state)

    buttons = [
        Button('back', handler=on_back_click),
        Button('quit', handler=exit_current_app)
    ]

    toolbar_keybindings = KeyBindings()

    @toolbar_keybindings.add('up')
    def _toolbar_on_key_up(_):
        app = get_app()
        difficulty_ui._selected_index = 0
        app.layout.focus(difficulty_ui)

    toolbar_content = Box(
        VSplit(
            children=buttons,
            align=HorizontalAlign.CENTER,
            padding=Dimension(preferred=10, max=10),
            key_bindings=merge_key_bindings([
                create_horizontal_button_list_keybindings(buttons),
                toolbar_keybindings
            ])
        ),
        height=1
    )

    return ToolbarFrame(body, toolbar_content, position=ToolbarFrameToolbarPosition.BOTTOM)


class QuestionComponent(ABC):
    @abstractmethod
    def render(self):
        pass

    def refocus(self):
        pass


class MultipleChoiceComponent(QuestionComponent):
    def __init__(self, controller, question, choices, correct_choice_index):
        self._controller = controller
        self._question = question
        self._choices = choices
        self._correct_choice_index = correct_choice_index

    def _create_choice_click_handler(self, choice_index):
        is_correct_choice_index = self._correct_choice_index == choice_index

        def on_choice_click():
            if is_correct_choice_index:
                pass
            pass

        return on_choice_click

    def render(self):
        question = self._question
        choices = self._choices

        buttons = [
            Button(
                '[%s] %s' % (i, choice_text),
                handler=self._create_choice_click_handler(i)
            ) for (i, choice_text) in zip(
                ascii_uppercase,
                choices,
            )
        ]

        first_button = buttons[0]
        self._first_button = first_button

        global global__default_target_focus
        global__default_target_focus = first_button

        keybindings = create_vertical_button_list_keybindings(buttons)
        is_first_button_selected = has_focus(first_button)

        @keybindings.add('up', filter=is_first_button_selected)
        def _first_button_on_key_up(_):
            focus_first_element()

        return Box(
            HSplit(
                [
                    TextArea(
                        text=question,
                        read_only=True,
                        focusable=False,
                        scrollbar=True,
                        # Push buttons to bottom of screen.
                        height=Dimension(preferred=100000, max=100000)
                    ),
                    HSplit(
                        [
                            VSplit(
                                children=[button],
                                align=HorizontalAlign.CENTER
                            ) for button in buttons
                        ],
                        padding=1,
                        key_bindings=keybindings
                    )
                ],
                padding=Dimension(preferred=2, max=2),
                width=Dimension(),
                align=VerticalAlign.TOP
            ),
            padding=1,
            style='bg:#88ff88 #000000'
        )

    def refocus(self):
        app = get_app()
        first_button = self._first_button
        app.layout.focus(first_button)


def number_theory_normal_bodmas(controller):
    difficulty = controller.state.session.settings.difficulty

    def add_parens(str):
        return '(%s)' % (str)

    def addition_op(lhs, rhs):
        (lhs_str, lhs_value, _) = lhs
        (rhs_str, rhs_value, _) = rhs
        new_str = '%s + %s' % (lhs_str, rhs_str)
        new_value = lhs_value + rhs_value
        return (new_str, new_value, False)

    def subtraction_op(lhs, rhs):
        (lhs_str, lhs_value, _) = lhs
        (rhs_str, rhs_value, is_rhs_grouped) = rhs
        new_str = '%s - %s' % (lhs_str,
                               rhs_str if is_rhs_grouped else add_parens(rhs_str))
        new_value = lhs_value - rhs_value
        return (new_str, new_value, False)

    def multiplication_op(lhs, rhs):
        (lhs_str, lhs_value, is_lhs_grouped) = lhs
        (rhs_str, rhs_value, is_rhs_grouped) = rhs
        new_str = '%s * %s' % (lhs_str if is_lhs_grouped else add_parens(
            lhs_str), rhs_str if is_rhs_grouped else add_parens(rhs_str))
        new_value = lhs_value * rhs_value
        return (new_str, new_value, new_value >= 0)

    # https://stackoverflow.com/questions/6800193/what-is-the-most-efficient-way-of-finding-all-the-factors-of-a-number-in-python
    def factors(n):
        return set(reduce(list.__add__,
                          ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))

    def division_op(dividend):
        (dividend_str, dividend_value, is_dividend_grouped) = dividend
        if dividend_value == 0:
            divisor = randint(1, 10)
        else:
            dividend_factors = factors(abs(dividend_value))
            divisor = random_choice(list(dividend_factors))
        new_str = '%s / %s' % (
            dividend_str if is_dividend_grouped else add_parens(dividend_str), divisor)
        new_value = dividend_value // divisor
        return (new_str, new_value, new_value >= 0)

    def power_op(base):
        (base_str, base_value, _) = base
        if base_value < 0:
            return None
        exponent = randint(1, 5 if base_value <=
                           2 else 3 if base_value <= 4 else 2)
        new_str = '%s^%s' % (
            base_str if base_str.isdigit() else add_parens(base_str), exponent)
        new_value = base_value ** exponent
        return (new_str, new_value, False)

    def negate_op(expr):
        (expr_str, expr_value, is_expr_grouped) = expr
        new_str = '-%s' % (expr_str if is_expr_grouped else add_parens(expr_str))
        new_value = -expr_value
        return (new_str, new_value, False)

    def parens_op(expr):
        (expr_str, expr_value, _) = expr
        if expr_str.isdigit():
            return None
        new_str = add_parens(expr_str)
        new_value = expr_value
        return (new_str, new_value, True)

    multi_ops = [
        addition_op,
        subtraction_op,
        multiplication_op,
    ]

    single_ops = [
        division_op,
        power_op,
        negate_op,
        parens_op,
    ]

    if difficulty == TestDifficultySetting.NORMAL:
        iterations = randint(3, 6)
    elif difficulty == TestDifficultySetting.HARD:
        iterations = randint(5, 8)

    def get_random_number_expr():
        number = randint(-10, 10)
        return (
            str(number),
            number,
            number > 0
        )

    expr = get_random_number_expr()
    previous_op = None

    while iterations > 0:
        if randint(0, 1) == 0:
            op = random_choice(multi_ops)
            if op == previous_op:
                continue
            random_expr = get_random_number_expr()
            if randint(0, 1) == 0:
                new_expr = op(expr, random_expr)
            else:
                new_expr = op(random_expr, expr)
        else:
            op = random_choice(single_ops)
            if op == previous_op:
                continue
            new_expr = op(expr)
        if new_expr == None:
            continue
        expr = new_expr
        iterations -= 1

    (expr_str, expr_value, _) = expr

    question = 'Evaluate %s' % (expr_str)

    fake_answer_range = (abs(expr_value) + 15)
    fake_answers = []
    while True:
        fake_answer = randint(-fake_answer_range, fake_answer_range)
        if fake_answer == expr_value or fake_answer in fake_answers:
            continue
        fake_answers.append(fake_answer)
        if len(fake_answers) == 3:
            break

    choices = [str(expr_value)] + fake_answers

    return MultipleChoiceComponent(controller, question, choices, 0)


QUESTION_BANK = {
    TestContentArea.NUMBER_THEORY: {
        TestDifficultySetting.NORMAL: [
            number_theory_normal_bodmas
        ],
        TestDifficultySetting.HARD: [
            number_theory_normal_bodmas
        ]
    },
    TestContentArea.ALGEBRA: {
        TestDifficultySetting.NORMAL: [
        ],
        TestDifficultySetting.HARD: [
        ],
    },
    TestContentArea.GEOMETRY: {
        TestDifficultySetting.NORMAL: [
        ],
        TestDifficultySetting.HARD: [
        ],
    }
}


def PlayingScreen(controller):
    session = controller.state.session
    difficulty = session.settings.difficulty
    # time_limit = session.settings.time_limit
    content = session.settings.content
    # question_count = session.settings.question_count

    content_area = random_choice(list(content))
    possible_questions = QUESTION_BANK[content_area][difficulty]
    make_question_component = random_choice(possible_questions)
    question_component = make_question_component(controller)

    def on_help_click():
        new_state = HelpScreenState(
            session=session,
            previous_state=controller.state
        )
        controller.set_state(new_state)

    def on_menu_click():
        new_state = MenuScreenState(session=session)
        controller.set_state(new_state)

    buttons = [
        Button('help', handler=on_help_click),
        Button('menu', handler=on_menu_click),
        Button('quit', handler=exit_current_app)
    ]

    toolbar_keybindings = create_horizontal_button_list_keybindings(buttons)
    is_button_focused = reduce(lambda a, b: a | b, map(has_focus, buttons))

    @toolbar_keybindings.add('down', filter=is_button_focused)
    def _toolbar_on_key_down(_):
        question_component.refocus()

    toolbar_content = Box(
        VSplit(
            children=buttons,
            align=HorizontalAlign.CENTER,
            key_bindings=toolbar_keybindings
        ),
        height=1
    )

    body = question_component.render()

    return ToolbarFrame(body, toolbar_content, position=ToolbarFrameToolbarPosition.TOP)


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

    if state.root_screen_type == RootScreenType.PLAYING:
        return PlayingScreen(controller)


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
    'dialog frame.label': 'bg:#000000 #00ff00',
    'dialog.body': 'bg:#000000 #00ff00',
    'dialog shadow': 'bg:#00aa00',
    'button.focused': 'bg:#228822'
})


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

    keybindings = KeyBindings()
    keybindings.add('tab')(focus_next)
    keybindings.add('s-tab')(focus_previous)

    @keybindings.add('c-c')
    def _on_key_ctrl_c(_):
        exit_current_app()

    return Application(
        layout=layout,
        key_bindings=keybindings,
        full_screen=True,
        mouse_support=True,
        after_render=ensure_focus,
        style=root_style
    )


def main():
    build_application().run()


if __name__ == "__main__":
    main()
