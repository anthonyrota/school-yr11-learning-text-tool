from abc import ABC, abstractmethod
from functools import reduce
from enum import Enum, auto
from time import time as get_cur_time
from string import ascii_lowercase, ascii_uppercase
from random import randint, uniform as randfloat, choice as random_choice, sample as random_sample, shuffle
from platform import system
from math import pi, sqrt

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
from prompt_toolkit.output.color_depth import ColorDepth
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


class SettingsScreenState:
    root_screen_type = RootScreenType.SETTINGS

    def __init__(self, session):
        self.session = session


class PlayingScreenState:
    root_screen_type = RootScreenType.PLAYING

    def __init__(self, session, test):
        self.session = session
        self.test = test


class Session:
    def __init__(self, username, settings):
        self.username = username
        self.settings = settings


class Test:
    def __init__(self, start_time, questions, question_index):
        self.start_time = start_time
        self.questions = questions
        self.question_index = question_index
        pass


class TestQuestion:
    def __init__(self, question_component, answer_state):
        self.question_component = question_component
        self.answer_state = answer_state
        pass


class TestQuestionAnswerStateType(Enum):
    NOT_ANSWERED = auto()
    ANSWERED_CORRECT = auto()
    ANSWERED_INCORRECT = auto()


class TestQuestionAnswerStateNotAnswered:
    type = TestQuestionAnswerStateType.NOT_ANSWERED


class TestQuestionAnswerStateAnsweredCorrect:
    type = TestQuestionAnswerStateType.ANSWERED_CORRECT

    def __init__(self, chosen_answer):
        self.chosen_answer = chosen_answer


class TestQuestionAnswerStateAnsweredIncorrect:
    type = TestQuestionAnswerStateType.ANSWERED_INCORRECT

    def __init__(self, chosen_answer):
        self.chosen_answer = chosen_answer


class TestSettings:
    def __init__(self, difficulty, content, question_count):
        self.difficulty = difficulty
        self.content = content
        self.question_count = question_count


class TestDifficultySetting(Enum):
    NORMAL = auto()
    HARD = auto()


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
        multiline=False,
        wrap_lines=False,
        accept_handler=on_accept,
        get_line_prefix=lambda line_number, wrap_count: '> ',
        style='bg:#88ff88 #000000 italic'
    )

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
                content=set((
                    TestContentArea.NUMBER_THEORY,
                    TestContentArea.ALGEBRA,
                    TestContentArea.GEOMETRY
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
        start_time = get_cur_time()
        new_state = PlayingScreenState(
            session=controller.state.session,
            test=Test(
                start_time=start_time,
                questions=make_questions(controller),
                question_index=0
            )
        )
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
        style='bg:#88ff88 #000000'
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
        (TestDifficultySetting.HARD, 'God Mode'),
    ])
    difficulty_ui.current_value = controller.state.session.settings.difficulty

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
                                Label(text=HTML('<b>Question Count</b>')),
                                question_count_ui
                            ],
                            padding=Dimension(preferred=1, max=1),
                        ),
                        HSplit(
                            [
                                Label(text=HTML('<b>Test Content</b>')),
                                content_ui,
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
    def render(self, update_question_answer_state):
        pass

    def refocus(self):
        pass


def get_is_test_current_question_answered(controller):
    test = controller.state.test
    return test.questions[test.question_index].answer_state.type != TestQuestionAnswerStateType.NOT_ANSWERED


class MultipleChoiceQuestion(QuestionComponent):
    def __init__(self, controller, question, choices, correct_choice_index):
        self._controller = controller
        self._question = question
        self._choices = choices
        self._correct_choice_index = correct_choice_index

    def render(self, update_question_answer_state):
        question = self._question
        choices = self._choices
        correct_choice_index = self._correct_choice_index
        is_answered = get_is_test_current_question_answered(self._controller)

        def make_choice_click_handler(choice_index):
            is_correct_choice_index = choice_index == correct_choice_index

            def on_choice_click():
                if is_answered:
                    return
                if is_correct_choice_index:
                    update_question_answer_state(
                        TestQuestionAnswerStateAnsweredCorrect(choice_index))
                else:
                    update_question_answer_state(
                        TestQuestionAnswerStateAnsweredIncorrect(choice_index))

            return on_choice_click

        test = self._controller.state.test
        answer_state = test.questions[test.question_index].answer_state

        def make_button(letter, i, choice_text):
            is_correct_answer = is_answered and i == correct_choice_index
            is_correct_chosen_answer = is_answered and i == correct_choice_index and answer_state.type == TestQuestionAnswerStateType.ANSWERED_CORRECT and answer_state.chosen_answer == i
            is_incorrect_chosen_answer = is_answered and i != correct_choice_index and answer_state.type == TestQuestionAnswerStateType.ANSWERED_INCORRECT and answer_state.chosen_answer == i

            return Button(
                '[%s] %s%s' % (letter, choice_text, ' ✓' if is_correct_chosen_answer else (
                    ' ✘' if is_incorrect_chosen_answer else '')),
                handler=make_choice_click_handler(i),
                focusable=not is_answered,
                class_='correct' if is_correct_answer else 'incorrect' if is_incorrect_chosen_answer else None
            )

        buttons = [
            make_button(letter, i, choice_text) for (letter, i, choice_text) in zip(
                ascii_uppercase,
                range(len(choices)),
                choices,
            )
        ]

        first_button = buttons[0]
        self._first_button = first_button

        global global__default_target_focus
        if not is_answered:
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
        if get_is_test_current_question_answered(self._controller):
            return
        app = get_app()
        first_button = self._first_button
        app.layout.focus(first_button)


class InputQuestion(QuestionComponent):
    def __init__(self, controller, question, get_input_error_msg, is_ans_correct, ex_correct_ans):
        self._controller = controller
        self._question = question
        self._get_input_error_msg = get_input_error_msg
        self._is_ans_correct = is_ans_correct
        self._ex_correct_ans = ex_correct_ans

    def render(self, update_question_answer_state):
        is_answered = get_is_test_current_question_answered(self._controller)
        error_msg = None

        def on_accept(buffer):
            if is_answered:
                return
            error = self._get_input_error_msg(textfield.text)
            if error:
                nonlocal error_msg
                error_msg = error
                app = get_app()
                app.invalidate()
            else:
                get_app().layout.focus(ok_button)
            return True  # Keeps text.

        def on_ok_clicked():
            if is_answered:
                return
            ans = textfield.text
            error = self._get_input_error_msg(ans)
            if error:
                nonlocal error_msg
                error_msg = error
                app = get_app()
                app.invalidate()
                return
            if self._is_ans_correct(ans):
                update_question_answer_state(
                    TestQuestionAnswerStateAnsweredCorrect(ans))
            else:
                update_question_answer_state(
                    TestQuestionAnswerStateAnsweredIncorrect(ans))

        test = self._controller.state.test
        answer_state = test.questions[test.question_index].answer_state
        is_answered_correct = answer_state.type == TestQuestionAnswerStateType.ANSWERED_CORRECT
        is_answered_incorrect = answer_state.type == TestQuestionAnswerStateType.ANSWERED_INCORRECT
        textfield = TextArea(
            multiline=False,
            wrap_lines=False,
            read_only=is_answered,
            focusable=not is_answered,
            accept_handler=on_accept,
            text=' ' + answer_state.chosen_answer +
            (' ✓' if is_answered_correct else ' ✘ answer is ' +
             self._ex_correct_ans) if is_answered else '',
            style=correct_style if is_answered_correct else incorrect_style if is_answered_incorrect else 'bg:#aaffaa #000000 italic',
            get_line_prefix=None if is_answered else lambda line_number, wrap_count: '> '
        )
        self._textfield = textfield
        ok_button = Button(text="Ok", handler=on_ok_clicked,
                           focusable=not is_answered)

        global global__default_target_focus
        if not is_answered:
            global__default_target_focus = textfield

        keybindings = KeyBindings()
        is_textfield_focused = has_focus(textfield)
        is_ok_button_focused = has_focus(ok_button)

        @keybindings.add('up', filter=is_textfield_focused)
        def _on_textfield_key_up(_):
            focus_first_element()

        @keybindings.add('down', filter=is_textfield_focused)
        def _on_textfield_key_down(_):
            app = get_app()
            app.layout.focus(ok_button)

        @keybindings.add('up', filter=is_ok_button_focused)
        def _on_ok_button_key_up(_):
            app = get_app()
            app.layout.focus(textfield)

        bottom_toolbar = ConditionalContainer(
            content=Box(
                VSplit(
                    children=[
                        DynamicContainer(
                            get_container=lambda: Label(text=error_msg or '', width=len(
                                error_msg) if error_msg else 0, dont_extend_height=True)
                        )
                    ],
                    align=HorizontalAlign.CENTER,
                    padding=Dimension(preferred=10, max=10),
                    style='#dd0000'
                ),
                height=1
            ),
            filter=renderer_height_is_known
        )

        bottom_group_children = [
            VSplit(
                [textfield],
                align=HorizontalAlign.CENTER
            )
        ]
        if not is_answered:
            bottom_group_children.append(VSplit(
                [ok_button],
                align=HorizontalAlign.CENTER
            ))

        return Box(
            HSplit(
                [
                    TextArea(
                        text=self._question,
                        read_only=True,
                        focusable=False,
                        scrollbar=True,
                        # Push input and ok button to bottom of screen.
                        height=Dimension(preferred=100000, max=100000)
                    ),
                    HSplit(
                        bottom_group_children,
                        padding=1,
                        key_bindings=keybindings,
                    ),
                    bottom_toolbar
                ],
                padding=Dimension(preferred=2, max=2),
                width=Dimension(),
                align=VerticalAlign.TOP
            ),
            padding=1,
            style='bg:#88ff88 #000000'
        )

    def refocus(self):
        if get_is_test_current_question_answered(self._controller):
            return
        app = get_app()
        textfield = self._textfield
        app.layout.focus(textfield)


def get_integer_error_msg(text):
    try:
        int(text)
        return None
    except ValueError:
        return 'Please enter an integer.'


def get_float_error_msg(text):
    try:
        float(text)
        return None
    except ValueError:
        return 'Please enter an valid number.'


def get_test_progress(controller, question_index):
    settings = controller.state.session.settings
    question_count = settings.question_count.value
    # Between 0 and 1.
    return question_index / (question_count-1)


# https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
def map_range(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def q_bodmas(controller, question_index):
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
        if base_value < 0 or base_value > 20:
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

    test_progress = get_test_progress(controller, question_index)
    if difficulty == TestDifficultySetting.NORMAL:
        difficulty_progression_factor = round(
            map_range(test_progress, 0, 1, 0, 4))
        iterations = randint(2+difficulty_progression_factor,
                             4+difficulty_progression_factor)
    elif difficulty == TestDifficultySetting.HARD:
        difficulty_progression_factor = round(
            map_range(test_progress, 0, 1, 0, 15))
        iterations = randint(5+difficulty_progression_factor,
                             10+difficulty_progression_factor)

    def get_random_number_expr():
        number = randint(-10, 10)
        return (
            str(number),
            number,
            number >= 0
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
        previous_op = op
        expr = new_expr
        iterations -= 1

    (expr_str, expr_value, _) = expr

    question = 'Evaluate %s' % (expr_str)

    if randint(0, 1) == 0:
        return InputQuestion(
            controller=controller,
            question=question,
            get_input_error_msg=get_integer_error_msg,
            is_ans_correct=lambda ans: ans == str(expr_value),
            ex_correct_ans=str(expr_value)
        )

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
    shuffle(choices)
    correct_choice_index = choices.index(str(expr_value))

    return MultipleChoiceQuestion(controller, question, choices, correct_choice_index)


def q_factorise_quadratic(controller, question_index):
    difficulty = controller.state.session.settings.difficulty

    test_progress = get_test_progress(controller, question_index)

    if difficulty == TestDifficultySetting.NORMAL:
        max_val = round(map_range(test_progress, 0, 1, 8, 20))
        k = 1
    else:
        max_val = round(map_range(test_progress, 0, 1, 25, 100))
        k = randint(1, max_val)
    a = randint(-max_val, max_val)
    b = randint(-max_val, max_val)
    x2_coeff = k
    x1_coeff = k*(a+b)
    x0_coeff = k*(a*b)
    poly = ('' if x2_coeff == 1 else str(x2_coeff)) + 'x^2'
    if x1_coeff != 0:
        poly += (' + ' if x1_coeff > 0 else ' - ') + \
            ('' if abs(x1_coeff) == 1 else str(abs(x1_coeff))) + 'x'
    if x0_coeff != 0:
        poly += (' + ' if x0_coeff > 0 else ' - ') + str(abs(x0_coeff))
    question = f'Factorise {poly} fully.'

    def make_factored_poly(a, b):
        def make_term(n):
            if n == 0:
                return 'x'
            return '(x'+('+' if n > 0 else '-')+str(abs(n))+')'
        a_term = make_term(a)
        b_term = make_term(b)
        return str('' if k == 1 else str(k))+(a_term+'^2' if a_term == b_term else b_term +
                                              a_term if b_term == 'x' else a_term+b_term)

    correct_ans = make_factored_poly(a, b)
    wrong_ans_error_range = (abs(a)+abs(b))//2+4
    choices = list(set((
        correct_ans,
        make_factored_poly(a+randint(-wrong_ans_error_range, wrong_ans_error_range),
                           b+randint(-wrong_ans_error_range, wrong_ans_error_range)),
        make_factored_poly(a+randint(-wrong_ans_error_range, wrong_ans_error_range),
                           b+randint(-wrong_ans_error_range, wrong_ans_error_range)),
        make_factored_poly(a+randint(-wrong_ans_error_range, wrong_ans_error_range),
                           b+randint(-wrong_ans_error_range, wrong_ans_error_range)),
    )))
    shuffle(choices)
    correct_choice_index = choices.index(correct_ans)

    return MultipleChoiceQuestion(controller, question, choices, correct_choice_index)


class PolyTerm:
    def __init__(self, variable, coeff, power):
        self.variable = variable
        self.coeff = coeff
        self.power = power  # Integer >= 0.


def poly_to_str(terms):
    poly_str = ''
    for term in terms:
        if term.coeff == 0:
            continue
        if term.coeff < 0:
            if poly_str == '':
                poly_str += '-'
            else:
                poly_str += ' - '
        elif poly_str != '':
            poly_str += ' + '
        if abs(term.coeff) != 1:
            poly_str += str(abs(term.coeff))
        if term.power == 0:
            continue
        if term.power == 1:
            poly_str += term.variable
        else:
            poly_str += term.variable + '^' + str(term.power)
    return poly_str


def q_simplify_linear(controller, question_index):
    difficulty = controller.state.session.settings.difficulty
    test_progress = get_test_progress(controller, question_index)
    if difficulty == TestDifficultySetting.NORMAL:
        variables = random_sample(population=['x', 'y'], k=randint(1, 2))
        coeff_range = round(map_range(test_progress, 0, 1, 12, 50))
        max_terms_per_var = round(map_range(test_progress, 0, 1, 2, 6))
    else:
        variables = random_sample(population=list(
            ascii_lowercase), k=randint(3, 8))
        coeff_range = round(map_range(test_progress, 0, 1, 1000, 3000))
        max_terms_per_var = round(map_range(test_progress, 0, 1, 5, 12))
    variable_coeffs = [[coeff * random_choice((-1, 1)) for coeff in random_sample(population=range(1, coeff_range), k=randint(
        2, max_terms_per_var))] for _ in variables]
    poly_q_terms = [PolyTerm(variable=variable, coeff=coeff, power=1) for (
        variable, coeffs) in zip(variables, variable_coeffs) for coeff in coeffs]
    shuffle(poly_q_terms)
    poly_q = poly_to_str(poly_q_terms)
    poly_ans_coeffs = [sum(coeffs) for coeffs in variable_coeffs]
    poly_ans_terms = [PolyTerm(variable=variable, coeff=coeff, power=1) for (
        variable, coeff) in zip(variables, poly_ans_coeffs)]
    correct_ans = poly_to_str(poly_ans_terms)

    def make_wrong_ans():
        def map_term(term):
            wrong_range = (abs(term.coeff) // 2) + 10
            return PolyTerm(variable=term.variable, coeff=term.coeff+randint(-wrong_range, wrong_range), power=term.power)
        return poly_to_str([map_term(term) for term in poly_ans_terms])
    choices = list(set([
        correct_ans,
        make_wrong_ans(),
        make_wrong_ans(),
        make_wrong_ans(),
    ]))
    shuffle(choices)
    correct_choice_index = choices.index(correct_ans)
    question = f'Simplify %s' % (poly_q)
    return MultipleChoiceQuestion(controller, question, choices, correct_choice_index)


def generate_pythag_triple_list():
    # https://stackoverflow.com/questions/575117/generating-unique-ordered-pythagorean-triplets
    def pythagore_triplets(n):
        maxn = int(n*(2**0.5))+1
        squares = [x*x for x in range(maxn+1)]
        reverse_squares = dict([(squares[i], i) for i in range(maxn+1)])
        for x in range(1, n):
            x2 = squares[x]
            for y in range(x, n+1):
                y2 = squares[y]
                z = reverse_squares.get(x2+y2)
                if z != None:
                    yield x, y, z

    return list(pythagore_triplets(2000))


pythag_triple_list = generate_pythag_triple_list()
units = ['mm', 'cm', 'm', 'km', ' miles', ' yoctometers', ' planck lengths']


def q_find_hypot(controller, question_index):
    difficulty = controller.state.session.settings.difficulty
    test_progress = get_test_progress(controller, question_index)
    if difficulty == TestDifficultySetting.NORMAL:
        upper_bound = round(map_range(test_progress, 0, 1, 15, 50))
    else:
        upper_bound = round(map_range(test_progress, 0, 1,
                                      500, len(pythag_triple_list)-1))
    i = randint(0, upper_bound)
    a, b, c = pythag_triple_list[i]
    unit = random_choice(units)
    question = f'What is the length of the hypotenuse in a right angled triangle with non-hypotenuse sides of length {a}{unit} and {b}{unit}?'
    d, e, f = pythag_triple_list[1 if i == 0 else i-1]
    choices = list(
        map(str, set((str(c)+unit, str(d)+unit, str(e)+unit, str(f)+unit))))
    shuffle(choices)
    correct_choice_index = choices.index(str(c)+unit)
    return MultipleChoiceQuestion(controller, question, choices, correct_choice_index)


def q_general_geometry(controller, question_index):
    difficulty = controller.state.session.settings.difficulty
    test_progress = get_test_progress(controller, question_index)

    def rand_progressive(min_upper, max_upper):
        difficulty_factor = 1 if difficulty == TestDifficultySetting.NORMAL else 100
        return randint(min_upper, round(map_range(test_progress, 0, 1, min_upper + (max_upper-min_upper)/5, max_upper * difficulty_factor)))

    def circle_area_from_radius(unit):
        radius = rand_progressive(5, 100)
        return (f'What is the area of a circle with radius {radius}{unit}', pi * radius**2)

    def circle_area_from_diameter(unit):
        diameter = rand_progressive(5, 200)
        return (f'What is the area of a circle with diameter {diameter}{unit}', pi * (diameter/2)**2)

    def circle_area_from_circumference(unit):
        circumference = rand_progressive(5, 600)
        radius = circumference/2/pi
        return (f'What is the area of a circle with circumference {circumference}{unit}', pi * radius**2)

    def circle_circumference_from_radius(unit):
        radius = rand_progressive(5, 100)
        return (f'What is the circumference of a circle with radius {radius}{unit}', 2*pi*radius)

    def circle_circumference_from_diameter(unit):
        diameter = rand_progressive(5, 200)
        return (f'What is the circumference of a circle with diameter {diameter}{unit}', 2*pi*(diameter/2))

    def circle_circumference_from_area(unit):
        area = rand_progressive(5, 10000)
        radius = sqrt(area/pi)
        return (f'What is the circumference of a circle with area {area}{unit}', 2*pi*radius)

    def circle_radius_from_diameter(unit):
        diameter = rand_progressive(5, 200)
        return (f'What is the radius of a circle with diameter {diameter}{unit}', diameter/2)

    def circle_radius_from_circumference(unit):
        circumference = rand_progressive(5, 600)
        return (f'What is the radius of a circle with circumference {circumference}{unit}', circumference/2/pi)

    def circle_radius_from_area(unit):
        area = rand_progressive(5, 10000)
        return (f'What is the radius of a circle with area {area}{unit}', sqrt(area/pi))

    def circle_diameter_from_radius(unit):
        radius = rand_progressive(5, 100)
        return (f'What is the diameter of a circle with radius {radius}{unit}', radius*2)

    def circle_diameter_from_circumference(unit):
        circumference = rand_progressive(5, 600)
        return (f'What is the diameter of a circle with circumference {circumference}{unit}', circumference/pi)

    def circle_diameter_from_area(unit):
        area = rand_progressive(5, 10000)
        return (f'What is the diameter of a circle with area {area}{unit}', sqrt(area/pi)*2)

    def square_perimeter_from_side_length(unit):
        side_length = rand_progressive(5, 100)
        return (f'What is the perimeter of a square with side length {side_length}{unit}', side_length * 4)

    def square_perimeter_from_area(unit):
        area = rand_progressive(5, 10000)
        return (f'What is the perimeter of a square with area {area}{unit}', sqrt(area)*4)

    def square_side_length_from_perimeter(unit):
        perimeter = rand_progressive(5, 400)
        return (f'What is the side length of a square with perimeter {perimeter}{unit}', perimeter/4)

    def square_side_length_from_area(unit):
        area = rand_progressive(5, 100000)
        return (f'What is the side length of a square with area {area}{unit}', sqrt(area))

    def square_area_from_side_length(unit):
        side_length = rand_progressive(5, 100)
        return (f'What is the area of a square with side length {side_length}{unit}', side_length**2)

    def square_area_from_perimeter(unit):
        perimeter = rand_progressive(5, 400)
        return (f'What is the area of a square with perimeter {perimeter}{unit}', (perimeter/4)**2)

    def rectangle_area_from_side_lengths(unit):
        a = rand_progressive(5, 100)
        b = rand_progressive(5, 100)
        return (f'What is the area of a rectangle with side lengths {a}{unit} and {b}{unit}', a*b)

    def rectangle_perimeter_from_side_lengths(unit):
        a = rand_progressive(5, 100)
        b = rand_progressive(5, 100)
        return (f'What is the perimeter of a rectangle with side lengths {a}{unit} and {b}{unit}', 2*(a+b))

    def triangle_area_from_base_height(unit):
        base = rand_progressive(5, 100)
        height = rand_progressive(5, 100)
        return (f'What is the area of a triangle with base {base}{unit} and height {height}{unit}', base*height/2)

    def trapezoid_area_from_top_bottom_height(unit):
        top = rand_progressive(5, 100)
        bottom = rand_progressive(5, 100)
        height = rand_progressive(5, 100)
        return (f'What is the area of a trapezoid with bottom side {bottom}{unit}, top side {top}{unit} and height {height}{unit}', (bottom+top)/2*height)

    def rhombus_area_from_diagonals(unit):
        p = rand_progressive(5, 100)
        q = rand_progressive(5, 100)
        return (f'What is the area of a rhombus with diagonals {p}{unit} and {q}{unit}', p*q/2)

    def kite_area_from_diagonals(unit):
        p = rand_progressive(5, 100)
        q = rand_progressive(5, 100)
        return (f'What is the area of a kite with diagonals {p}{unit} and {q}{unit}', p*q/2)

    q_factories = [
        circle_area_from_radius,
        circle_area_from_diameter,
        circle_area_from_circumference,
        circle_circumference_from_radius,
        circle_circumference_from_diameter,
        circle_circumference_from_area,
        circle_radius_from_diameter,
        circle_radius_from_circumference,
        circle_radius_from_area,
        circle_diameter_from_radius,
        circle_diameter_from_circumference,
        circle_diameter_from_area,
        square_perimeter_from_side_length,
        square_perimeter_from_area,
        square_side_length_from_perimeter,
        square_side_length_from_area,
        square_area_from_side_length,
        square_area_from_perimeter,
        rectangle_area_from_side_lengths,
        rectangle_perimeter_from_side_lengths,
        triangle_area_from_base_height,
        trapezoid_area_from_top_bottom_height,
        rhombus_area_from_diagonals,
        kite_area_from_diagonals,
    ]

    q_factory = random_choice(q_factories)
    unit = random_choice(units)
    (question, exact_ans) = q_factory(unit)
    dp = 0 if float(exact_ans).is_integer() else randint(0, 4)

    # https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
    def roundTraditional(val, digits):
        return round(val+10**(-len(str(val))-1), digits)

    correct_ans = float(roundTraditional(exact_ans, dp))
    question += f' to the nearest {unit.lstrip().rstrip("s")}?' if dp == 0 else f' to {dp} decimal place{"" if dp == 1 else "s"}?'

    def num_to_str(num):
        return '%.*f' % (dp, num)

    if randint(0, 1) == 0:
        return InputQuestion(
            controller=controller,
            question=question,
            get_input_error_msg=get_float_error_msg,
            is_ans_correct=lambda num: num_to_str(
                float(num)) == num_to_str(correct_ans),
            ex_correct_ans=num_to_str(correct_ans)
        )

    fake_answer_min = round(correct_ans / 3) + 1
    fake_answer_max = round(correct_ans * 3) + 1
    fake_answers = []

    while True:
        if correct_ans.is_integer():
            fake_answer = randint(fake_answer_min, fake_answer_max)
        else:
            fake_answer = roundTraditional(
                randfloat(fake_answer_min, fake_answer_max), dp)
        if fake_answer == correct_ans or fake_answer in fake_answers:
            continue
        fake_answers.append(fake_answer)
        if len(fake_answers) == 3:
            break

    choices = [num_to_str(num)+unit for num in ([correct_ans] + fake_answers)]
    shuffle(choices)
    correct_choice_index = choices.index(num_to_str(correct_ans)+unit)

    return MultipleChoiceQuestion(controller, question, choices, correct_choice_index)


QUESTION_BANK = {
    TestContentArea.NUMBER_THEORY: {
        TestDifficultySetting.NORMAL: [
            q_bodmas
        ],
        TestDifficultySetting.HARD: [
            q_bodmas
        ]
    },
    TestContentArea.ALGEBRA: {
        TestDifficultySetting.NORMAL: [
            q_factorise_quadratic,
            q_simplify_linear
        ],
        TestDifficultySetting.HARD: [
            q_factorise_quadratic,
            q_simplify_linear
        ],
    },
    TestContentArea.GEOMETRY: {
        TestDifficultySetting.NORMAL: [
            q_find_hypot,
            # Multiple times to increase probability of being chosen.
            q_general_geometry,
            q_general_geometry,
            q_general_geometry,
            q_general_geometry
        ],
        TestDifficultySetting.HARD: [
            q_find_hypot,
            q_general_geometry,
            q_general_geometry,
            q_general_geometry,
            q_general_geometry
        ],
    }
}


def make_questions(controller):
    settings = controller.state.session.settings
    difficulty = settings.difficulty
    content = settings.content
    question_count = settings.question_count

    def make_question(question_index):
        content_area = random_choice(list(content))
        possible_questions = QUESTION_BANK[content_area][difficulty]
        make_question_component = random_choice(possible_questions)
        question_component = make_question_component(
            controller, question_index)
        return TestQuestion(
            question_component=question_component,
            answer_state=TestQuestionAnswerStateNotAnswered()
        )

    return [make_question(i) for i in range(question_count.value)]


def format_time(time):
    m, s = divmod(round(time), 60)
    h, m = divmod(m, 60)

    return 'Hours: %s, Minutes: %s, Seconds: %s' % (h, m, s)


def FinishScreen(controller):
    session = controller.state.session
    test = controller.state.test
    questions_count = session.settings.question_count
    questions_right = sum(1 if question.answer_state.type ==
                          TestQuestionAnswerStateType.ANSWERED_CORRECT else 0 for question in test.questions)

    start_time = test.start_time
    current_time = get_cur_time()
    time_played = current_time - start_time
    time_played_formatted = format_time(time_played)

    text = "Congratulations! You reached the end of the test. You scored %s/%s.\n\nTime Taken:\n%s" % (
        questions_right, questions_count.value, time_played_formatted)

    def on_back_click():
        new_state = PlayingScreenState(
            session=session,
            test=Test(
                start_time=test.start_time,
                questions=test.questions,
                question_index=len(test.questions)-1
            )
        )
        controller.set_state(new_state)

    def on_help_click():
        new_state = HelpScreenState(
            session=session,
            previous_state=controller.state
        )
        controller.set_state(new_state)

    toolbar_buttons = [
        Button('(back)', handler=on_back_click),
        Button('help', handler=on_help_click),
        Button('quit', handler=exit_current_app)
    ]

    toolbar_keybindings = create_horizontal_button_list_keybindings(
        toolbar_buttons)

    @toolbar_keybindings.add('down')
    def _toolbar_on_down(_):
        app = get_app()
        app.layout.focus(main_buttons[0])

    toolbar_content = Box(
        VSplit(
            children=toolbar_buttons,
            align=HorizontalAlign.CENTER,
            key_bindings=toolbar_keybindings
        ),
        height=1
    )

    def on_menu_click():
        new_state = MenuScreenState(session=session)
        controller.set_state(new_state)

    def on_retry_test_click():
        start_time = get_cur_time()
        new_questions = [TestQuestion(question_component=question.question_component,
                                      answer_state=TestQuestionAnswerStateNotAnswered()) for question in test.questions]
        new_state = PlayingScreenState(
            session=session,
            test=Test(
                start_time=start_time,
                questions=new_questions,
                question_index=0
            )
        )
        controller.set_state(new_state)

    def on_retry_incorrect_questions_click():
        def map_question(question):
            if question.answer_state.type == TestQuestionAnswerStateType.ANSWERED_INCORRECT:
                return TestQuestion(question_component=question.question_component, answer_state=TestQuestionAnswerStateNotAnswered())
            return question

        for i, question in enumerate(test.questions):
            if question.answer_state.type == TestQuestionAnswerStateType.ANSWERED_INCORRECT:
                first_incorrect_question_index = i
                break
        new_questions = [map_question(question) for question in test.questions]
        new_state = PlayingScreenState(
            session=session,
            test=Test(
                start_time=test.start_time,
                questions=new_questions,
                question_index=first_incorrect_question_index
            )
        )
        controller.set_state(new_state)

    main_buttons = [
        Button('back to menu', handler=on_menu_click),
        Button('retry test', handler=on_retry_test_click)
    ]

    if questions_right != questions_count.value:
        main_buttons.append(Button('retry incorrect questions',
                                   handler=on_retry_incorrect_questions_click))

    global global__default_target_focus
    global__default_target_focus = main_buttons[0]

    main_keybindings = create_vertical_button_list_keybindings(main_buttons)

    @main_keybindings.add('up', filter=has_focus(main_buttons[0]))
    def _first_main_button_on_key_up(_):
        focus_first_element()

    body = Box(
        HSplit(
            [
                TextArea(
                    text=text,
                    read_only=True,
                    focusable=False,
                    scrollbar=True,
                ),
                HSplit(
                    [
                        VSplit(
                            children=[button],
                            align=HorizontalAlign.CENTER
                        ) for button in main_buttons
                    ],
                    padding=1,
                    key_bindings=main_keybindings
                )
            ],
            padding=Dimension(preferred=2, max=2),
            width=Dimension(),
            align=VerticalAlign.TOP
        ),
        padding=1,
        style='bg:#88ff88 #000000'
    )

    return ToolbarFrame(body, toolbar_content, position=ToolbarFrameToolbarPosition.TOP)


def PlayingScreen(controller):
    session = controller.state.session
    test = controller.state.test
    question_index = test.question_index

    if test.question_index == len(test.questions):
        return FinishScreen(controller)

    current_question = test.questions[question_index]
    current_question_component = current_question.question_component

    def update_question_answer_state(answer_state):
        new_current_question = TestQuestion(
            question_component=current_question_component,
            answer_state=answer_state
        )
        new_questions = test.questions.copy()
        new_questions[test.question_index] = new_current_question
        new_state = PlayingScreenState(
            session=session,
            test=Test(
                start_time=test.start_time,
                questions=new_questions,
                question_index=test.question_index
            )
        )
        controller.set_state(new_state)

    body = current_question_component.render(update_question_answer_state)

    def on_back_click():
        new_state = PlayingScreenState(
            session=session,
            test=Test(
                start_time=test.start_time,
                questions=test.questions,
                question_index=test.question_index-1
            )
        )
        controller.set_state(new_state)

    def on_next_click():
        new_state = PlayingScreenState(
            session=session,
            test=Test(
                start_time=test.start_time,
                questions=test.questions,
                question_index=test.question_index+1
            )
        )
        controller.set_state(new_state)

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

    if test.question_index > 0:
        buttons.insert(
            0, Button('(back)', handler=on_back_click))

    if test.question_index == len(test.questions) - 1:
        buttons.append(Button('(finish test)', handler=on_next_click))
    else:
        buttons.append(Button('(next)', handler=on_next_click))

    if current_question.answer_state.type != TestQuestionAnswerStateType.NOT_ANSWERED:
        global global__default_target_focus
        global__default_target_focus = buttons[-1]

    toolbar_keybindings = create_horizontal_button_list_keybindings(buttons)
    is_button_focused = reduce(lambda a, b: a | b, map(has_focus, buttons))

    @toolbar_keybindings.add('down', filter=is_button_focused)
    def _toolbar_on_key_down(_):
        current_question_component.refocus()

    question_label_text = 'Q%s.' % (question_index+1)
    toolbar_content = Box(
        VSplit(
            children=[Label(text=question_label_text, dont_extend_height=True, width=len(
                question_label_text)+3)] + buttons,
            align=HorizontalAlign.CENTER,
            key_bindings=toolbar_keybindings
        ),
        height=1
    )

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


correct_style = 'bg:#00aa00'
incorrect_style = 'bg:#dd0000'

root_style = Style.from_dict({
    'dialog': 'bg:#88ff88',
    'dialog frame.label': 'bg:#000000 #00ff00',
    'dialog.body': 'bg:#000000 #00ff00',
    'dialog shadow': 'bg:#00aa00',
    'button.focused': 'bg:#228822',
    'correct': correct_style,
    'incorrect': incorrect_style,
    'dialog.body text-area last-line': 'nounderline'
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
        style=root_style,
        color_depth=ColorDepth.DEPTH_24_BIT if system() == 'Windows' else None
    )


def main():
    build_application().run()


if __name__ == "__main__":
    main()
