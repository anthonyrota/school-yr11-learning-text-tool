from pyflowchart import Flowchart, StartNode, OperationNode, ConditionNode, InputOutputNode, SubroutineNode, EndNode
import json


def start_subr():
    begin = StartNode('BEGIN')
    begin \
        .connect(OperationNode('import standard library helpers')) \
        .connect(OperationNode('import prompt toolkit library')) \
        .connect(OperationNode('UI set state UsernameScreenState')) \
        .connect(EndNode('END'))
    return [begin]


def get_username_subr():
    begin = StartNode('BEGIN SetUsernameScreen')

    def is_username_valid_subr():
        begin = StartNode('BEGIN is_username_valid')
        begin \
            .connect(OperationNode('is_valid = username length > 0')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN is_valid')) \
            .connect(EndNode('END is_username_valid'))
        return begin

    username_input = begin.connect(
        InputOutputNode(InputOutputNode.INPUT, 'username = UI get username')
    )
    is_valid_cond = username_input \
        .connect(SubroutineNode('is_valid = is_username_valid(username)')) \
        .connect(ConditionNode('IF is_valid'))
    is_valid_cond.connect_yes(
        OperationNode('session = Session(username, default_settings)')
    ) \
        .connect(OperationNode('new_state = MenuScreenState(session)')) \
        .connect(OperationNode('UI set state new_state')) \
        .connect(EndNode('END SetUsernameScreen'))
    is_valid_cond.connect_no(username_input)

    return [begin, is_username_valid_subr()]


def menu_subr():
    begin = StartNode('BEGIN MenuScreen')

    def on_start_click_subr():
        begin = StartNode('BEGIN on_start_click')
        begin \
            .connect(SubroutineNode('start_time = get_cur_time()')) \
            .connect(SubroutineNode('questions = make_questions()')) \
            .connect(OperationNode('test = Test(start_time, questions, question_index=0)')) \
            .connect(OperationNode('new_state = PlayingScreenState(session, test)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_start_click'))
        return begin

    def on_settings_click_subr():
        begin = StartNode('BEGIN on_settings_click')
        begin \
            .connect(OperationNode('new_state = SettingsScreenState(session)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_settings_click'))
        return begin

    def on_help_click_subr():
        begin = StartNode('BEGIN on_help_click')
        begin \
            .connect(OperationNode('new_state = HelpScreenState(session, previous_state=state)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_help_click'))
        return begin

    begin \
        .connect(OperationNode('UI set menu ui')) \
        .connect(OperationNode('UI on start button click call on_start_click')) \
        .connect(OperationNode('UI on settings button click call on_settings_click')) \
        .connect(OperationNode('UI on help button click call on_help_click')) \
        .connect(EndNode('END MenuScreen'))

    return [begin, on_start_click_subr(), on_settings_click_subr(), on_help_click_subr()]


def help_subr():
    begin = StartNode('BEGIN HelpScreen')

    def on_back_click_subr():
        begin = StartNode('BEGIN on_back_click')
        begin \
            .connect(OperationNode('new_state = previous_state')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_back_click'))
        return begin

    begin \
        .connect(OperationNode('UI set help ui')) \
        .connect(OperationNode('UI on back button click call on_back_click')) \
        .connect(EndNode('END HelpScreen'))

    return [begin, on_back_click_subr()]


def settings_subr():
    begin = StartNode('BEGIN SettingsScreen')

    def on_back_click_subr():
        begin = StartNode('BEGIN on_back_click')
        cond = begin.connect(
            ConditionNode('length of set of content areas chosen == 0')
        )
        cond \
            .connect_yes(OperationNode('UI focus content area picker')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN'))
        cond \
            .connect_no(OperationNode('settings = TestSettings(difficulty, content, question_count)')) \
            .connect(OperationNode('session = Session(username, settings)')) \
            .connect(OperationNode('new_state = MenuScreenState(session)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_back_click'))
        return begin

    begin \
        .connect(OperationNode('UI set settings ui')) \
        .connect(OperationNode('UI on back button click call on_back_click'))

    return [begin, on_back_click_subr()]


def get_is_test_current_question_answered_subr():
    begin = StartNode('BEGIN get_is_test_current_question_answered')
    begin \
        .connect(OperationNode('is_answered = questions[question_index] answer state type is not NOT_ANSWERED')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN is_answered')) \
        .connect(EndNode('END get_is_test_current_question_answered'))
    return [begin]


def MultipleChoiceQuestion_subr():
    begin = StartNode('BEGIN class MultipleChoiceQuestion')

    def on_choice_click_subr():
        begin = StartNode('BEGIN on_choice_click')
        cond = begin.connect(ConditionNode('IF is_answered'))
        cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN'))
        cond = cond.connect_no(ConditionNode('IF is choice correct'))
        cond.connect_yes(SubroutineNode(
            'update_question_answer_state(answered correct)'))
        cond \
            .connect_no(SubroutineNode('update_question_answer_state(answered incorrect)')) \
            .connect(EndNode('END on_choice_click'))
        return begin

    def render_subr():
        begin = StartNode('BEGIN MultipleChoiceQuestion#render')
        begin \
            .connect(SubroutineNode('is_answered = get_is_test_current_question_answered(controller)')) \
            .connect(OperationNode('UI set multiple choice question ui')) \
            .connect(OperationNode('UI on answer chosen call on_choice_click')) \
            .connect(EndNode('END MultipleChoiceQuestion#render'))
        return begin

    begin \
        .connect(OperationNode('set instance controller value')) \
        .connect(OperationNode('set instance question value')) \
        .connect(OperationNode('set instance choices value')) \
        .connect(OperationNode('set instance correct_choice_index value')) \
        .connect(EndNode('END class MultipleChoiceQuestion'))

    return [begin, render_subr(), on_choice_click_subr()]


def InputQuestion_subr():
    begin = StartNode('BEGIN class InputQuestion')

    def on_accept_subr():
        begin = StartNode('BEGIN on_accept')
        cond = begin.connect(ConditionNode('IF is_answered'))
        cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN'))
        cond = cond \
            .connect_no(SubroutineNode('error = get_input_error_msg(textfield text)')) \
            .connect(ConditionNode('IF error'))
        cond \
            .connect_yes(OperationNode('UI set error msg to error')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'return True # Returning true keeps text.'))
        cond \
            .connect_no(OperationNode('UI focus ok button')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'return True # Returning true keeps text.')) \
            .connect(EndNode('END on_accept'))
        return begin

    def on_ok_clicked_subr():
        begin = StartNode('BEGIN on_ok_clicked')
        cond = begin.connect(ConditionNode('IF is_answered'))
        cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN'))
        cond = cond \
            .connect_no(SubroutineNode('error = get_input_error_msg(textfield text)')) \
            .connect(ConditionNode('IF error'))
        cond \
            .connect_yes(OperationNode('UI set error msg to error')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN'))
        cond = cond \
            .connect_no(SubroutineNode('is_correct = is_ans_correct(textfield text)')) \
            .connect(ConditionNode('IF is_correct'))
        cond.connect_yes(SubroutineNode(
            'update_question_answer_state(answered correct)'))
        cond \
            .connect_no(SubroutineNode('update_question_answer_state(answered incorrect)')) \
            .connect(EndNode('END on_ok_clicked'))
        return begin

    def render_subr():
        begin = StartNode('BEGIN InputQuestion#render')
        begin \
            .connect(SubroutineNode('is_answered = get_is_test_current_question_answered(controller)')) \
            .connect(OperationNode('UI set input question ui')) \
            .connect(OperationNode('UI on input enter key call on_accept')) \
            .connect(OperationNode('UI on ok button click call on_ok_clicked')) \
            .connect(EndNode('END InputQuestion#render'))
        return begin

    begin \
        .connect(OperationNode('set instance controller value')) \
        .connect(OperationNode('set instance question value')) \
        .connect(OperationNode('set instance get_input_error_msg value')) \
        .connect(OperationNode('set instance is_ans_correct value')) \
        .connect(OperationNode('set instance ex_correct_ans value # example correct')) \
        .connect(EndNode('END class MultipleChoiceQuestion'))

    return [begin, render_subr(), on_accept_subr(), on_ok_clicked_subr()]


def get_integer_error_msg_subr():
    begin = StartNode('BEGIN get_integer_error_msg')
    cond = begin \
        .connect(OperationNode('TRY convert text to int')) \
        .connect(ConditionNode('IF error when converting'))
    cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN None'))
    cond \
        .connect_no(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN "Please enter an integer."')) \
        .connect(EndNode('END get_integer_error_msg'))
    return [begin]


def get_float_error_msg_subr():
    begin = StartNode('BEGIN get_float_error_msg')
    cond = begin \
        .connect(OperationNode('TRY convert text to float')) \
        .connect(ConditionNode('IF error when converting'))
    cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN None'))
    cond \
        .connect_no(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN "Please enter a valid number."')) \
        .connect(EndNode('END get_float_error_msg'))
    return [begin]


def get_test_progress_subr():
    begin = StartNode('BEGIN get_test_progress')
    begin \
        .connect(OperationNode('progress = question_index / (question_count - 1)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN progress')) \
        .connect(EndNode('END get_test_progress'))
    return [begin]


def map_range_subr():
    begin = StartNode('BEGIN map_range')
    begin \
        .connect(OperationNode('leftSpan = leftMax - leftMin')) \
        .connect(OperationNode('rightSpan = rightMax - rightMin')) \
        .connect(OperationNode('valueScaled = (value - leftMin) / leftSpan')) \
        .connect(OperationNode('result = rightMin + (valueScaled * rightSpan)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN result')) \
        .connect(EndNode('END map_range'))
    return [begin]


def q_bodmas_subr():
    begin = StartNode('BEGIN q_bodmas')

    def add_parens_subr():
        begin = StartNode('BEGIN add_parens')
        begin \
            .connect(OperationNode('result = "(" + string + ")"')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN result')) \
            .connect(EndNode('END add_parens'))
        return begin

    def addition_op_subr():
        begin = StartNode('BEGIN addition_op')
        begin \
            .connect(OperationNode('new_str = concatenate lhs_str, " + ", rhs_str but wrapped in parens if begins with "-"')) \
            .connect(OperationNode('new_value = lhs_value + rhs_value')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN new_str, new_value, False')) \
            .connect(EndNode('END addition_op'))
        return begin

    def subtraction_op_subr():
        begin = StartNode('BEGIN subtraction_op')
        begin \
            .connect(OperationNode('new_str = concatenate lhs_str, " - ", rhs_str but wrapped in parens if not grouped')) \
            .connect(OperationNode('new_value = lhs_value - rhs_value')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN new_str, new_value, False')) \
            .connect(EndNode('END subtraction_op'))
        return begin

    def multiplication_op_subr():
        begin = StartNode('BEGIN multiplication_op')
        begin \
            .connect(OperationNode('new_str = concatenate lhs_str but wrapped in parens if not grouped, " × ", rhs_str but wrapped in parens if not grouped')) \
            .connect(OperationNode('new_value = lhs_value * rhs_value')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN new_str, new_value, True')) \
            .connect(EndNode('END multiplication_op'))
        return begin

    def factors_subr():
        begin = StartNode('BEGIN factors')
        begin \
            .connect(OperationNode('result = get factors of n using stackoverflow magic')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN result')) \
            .connect(EndNode('END factors'))
        return begin

    def division_op_subr():
        begin = StartNode('BEGIN division_op')
        cond = begin.connect(ConditionNode('IF dividend_value == 0'))
        yes = cond.connect_yes(OperationNode(
            'divisor = random integer from 1 to 10'))
        no = cond \
            .connect_no(SubroutineNode('dividend_factors = factors(dividend_value but positive)')) \
            .connect(OperationNode('divisor = choose random factor from dividend_factors'))
        op = OperationNode(
            'new_str = concatenate dividend_str but wrapped in parens if not grouped, " ÷ ", divisor')
        yes.connect(op)
        no.connect(op)
        op \
            .connect(OperationNode('new_value = dividend_value / divisor')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN new_str, new_value, True')) \
            .connect(EndNode('END division_op'))
        return begin

    def power_op_subr():
        begin = StartNode('BEGIN power_op')
        cond = begin.connect(ConditionNode(
            'IF base_value < 0 or base_value > 20'))
        cond.connect_yes(InputOutputNode(
            InputOutputNode.OUTPUT, 'RETURN None'))
        cond \
            .connect_no(OperationNode('max_exponent = 5 if base_value <= 2 else 3 if base_value <= 4 else 2')) \
            .connect(OperationNode('exponent = randint from 1 to max_exponent')) \
            .connect(OperationNode('new_str = concatenate base_str but wrapped in parens if not a num, exponent translated to superscript')) \
            .connect(OperationNode('new_value = base_value ** exponent')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN new_str, new_value, True')) \
            .connect(EndNode('END power_op'))
        return begin

    def negate_op_subr():
        begin = StartNode('BEGIN negate_op')
        begin \
            .connect(OperationNode('new_str = concatenate "-", expr_str but wrapped in parens if not grouped')) \
            .connect(OperationNode('new_value = -expr_value')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN new_str, new_value, False')) \
            .connect(EndNode('END negate_op'))
        return begin

    def parens_op_subr():
        begin = StartNode('BEGIN parens_op')
        cond = begin.connect(ConditionNode('IF expr_str is a num'))
        cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN'))
        cond \
            .connect_no(SubroutineNode('new_str = add_parens(expr_str)')) \
            .connect(OperationNode('new_value = expr_value')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN new_str, new_value, True')) \
            .connect(EndNode('END parens_op'))
        return begin

    def get_random_number_expr_subr():
        begin = StartNode('BEGIN get_random_number_expr')
        begin \
            .connect(OperationNode('number = randint from -10 to 10')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN number as string, number, number >= 0')) \
            .connect(EndNode('END get_random_number_expr'))
        return begin

    cond = begin \
        .connect(OperationNode('multi_ops = [addition_op, subtraction_op, multiplication_op]')) \
        .connect(OperationNode('single_ops = [division_op, power_op, negate_op, parens_op]')) \
        .connect(SubroutineNode('test_progress = get_test_progress(controller, question_index)')) \
        .connect(ConditionNode('IF difficulty is normal'))
    yes = cond.connect_yes(SubroutineNode(
        'difficulty_progression_factor = round result of map_range(test_progress, 0, 1, 0, 4)'))
    yes.connect(OperationNode(
        'iterations = randint from (2+difficulty_progression_factor) to (4+difficulty_progression_factor)'))
    no = cond.connect_no(SubroutineNode(
        'difficulty_progression_factor = round result of map_range(test_progress, 0, 1, 0, 15)'))
    no.connect(OperationNode(
        'iterations = randint from (5+difficulty_progression_factor) to (10+difficulty_progression_factor)'))
    subr = SubroutineNode('expr = get_random_number_expr()') \
        .connect(OperationNode('previous_op = None'))
    yes.connect(subr)
    no.connect(subr)
    while_cond = subr.connect(ConditionNode('IF iterations > 0'))
    out_cond = while_cond.connect_yes(
        ConditionNode('IF randint from 0-1 == 0'))
    cond = out_cond \
        .connect_yes(OperationNode('op = choose random op from multi_ops')) \
        .connect(ConditionNode('IF op == previous_op'))
    cond.connect_yes(while_cond)
    loop_tail = OperationNode('previous_op = op')
    loop_tail_cond = loop_tail.connect(ConditionNode('IF new_expr is None'))
    loop_tail_cond.connect_yes(while_cond)
    loop_tail_cond \
        .connect_no(OperationNode('expr = new_expr')) \
        .connect(OperationNode('iterations -= 1')) \
        .connect(while_cond)
    cond = cond \
        .connect_no(SubroutineNode('random_expr = get_random_number_expr()')) \
        .connect(ConditionNode('IF randint from 0-1 == 0'))
    cond \
        .connect_yes(OperationNode('new_expr = op(expr, random_expr)')) \
        .connect(loop_tail)
    cond \
        .connect_no(OperationNode('new_expr = op(random_expr, expr)')) \
        .connect(loop_tail)
    cond = out_cond \
        .connect_no(OperationNode('op = random_choice(single_ops)')) \
        .connect(ConditionNode('IF op == previous_op'))
    cond.connect_yes(while_cond)
    cond \
        .connect_no(OperationNode('new_expr = op(expr)')) \
        .connect(loop_tail)
    cond = while_cond \
        .connect_no(OperationNode('question = concatenate "Evaluate ", expr_str')) \
        .connect(ConditionNode('IF randint from 0-1 == 0'))
    cond \
        .connect_yes(OperationNode('is_ans_correct = lambda ans: ans == expr_value as string')) \
        .connect(OperationNode('component = InputQuestion(controller, question, get_integer_error_msg, is_ans_correct, expr_value as string)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN component'))
    while_anchor = cond \
        .connect_no(OperationNode('fake_answer_range = (expr_value but positive) + 15')) \
        .connect(OperationNode('fake_answers = []')) \
        .connect(OperationNode('fake_answer = randint from -fake_answer_range to fake_answer_range'))
    cond = while_anchor.connect(ConditionNode(
        'IF fake_answer == expr_value or fake_answer in fake_answers'))
    cond.connect_yes(while_anchor)
    cond = cond \
        .connect_no(OperationNode('add fake_answer to fake_answers')) \
        .connect(ConditionNode('IF fake_answers length == 3'))
    cond.connect_no(while_anchor)
    cond \
        .connect_yes(OperationNode('choices = list with str(expr_value) concatenated with fake_answers')) \
        .connect(OperationNode('shuffle choices')) \
        .connect(OperationNode('correct_choice_index = get index of str(expr_value) in choices')) \
        .connect(OperationNode('component = MultipleChoiceQuestion(controller, question, choices, correct_choice_index)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN component'))

    return [
        begin,
        add_parens_subr(),
        addition_op_subr(),
        subtraction_op_subr(),
        multiplication_op_subr(),
        factors_subr(),
        division_op_subr(),
        power_op_subr(),
        negate_op_subr(),
        parens_op_subr(),
        get_random_number_expr_subr()
    ]


print(json.dumps([
    [Flowchart(fc).flowchart() for fc in fcg] for fcg in (
        start_subr(),
        get_username_subr(),
        menu_subr(),
        help_subr(),
        settings_subr(),
        get_is_test_current_question_answered_subr(),
        MultipleChoiceQuestion_subr(),
        InputQuestion_subr(),
        get_integer_error_msg_subr(),
        get_float_error_msg_subr(),
        get_test_progress_subr(),
        map_range_subr(),
        q_bodmas_subr()
    )
]))
