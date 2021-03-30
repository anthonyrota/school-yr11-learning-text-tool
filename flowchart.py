from pyflowchart import Flowchart, StartNode, OperationNode, ConditionNode, InputOutputNode, SubroutineNode, EndNode
import json


def start_subr():
    begin = StartNode('BEGIN')
    begin \
        .connect(OperationNode('import standard library utils')) \
        .connect(OperationNode('import prompt toolkit library')) \
        .connect(OperationNode('units = ["mm", "cm", "m", "km", " miles", " yoctometers", " planck lengths"]')) \
        .connect(OperationNode('UI setup root controller with renderer RootScreen')) \
        .connect(OperationNode('UI setup keybindings, focus management and styling')) \
        .connect(OperationNode('UI set state UsernameScreenState')) \
        .connect(OperationNode('UI setup prompt_toolkit application')) \
        .connect(OperationNode('UI run application if is main file')) \
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
        .connect(OperationNode('UI on back button click call on_back_click')) \
        .connect(EndNode('END SettingsScreen'))

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
        .connect(EndNode('END class InputQuestion'))

    return [begin, render_subr(), on_accept_subr(), on_ok_clicked_subr()]


def get_integer_error_msg_subr():
    begin = StartNode('BEGIN get_integer_error_msg')
    cond = begin \
        .connect(OperationNode('TRY convert text to int')) \
        .connect(ConditionNode('IF error when converting'))
    cond.connect_no(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN None'))
    cond \
        .connect_yes(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN "Please enter an integer."')) \
        .connect(EndNode('END get_integer_error_msg'))
    return [begin]


def get_float_error_msg_subr():
    begin = StartNode('BEGIN get_float_error_msg')
    cond = begin \
        .connect(OperationNode('TRY convert text to float')) \
        .connect(ConditionNode('IF error when converting'))
    cond.connect_no(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN None'))
    cond \
        .connect_yes(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN "Please enter a valid number."')) \
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

    def get_q_expr_subr():
        begin = StartNode('BEGIN get_q_expr')
        subr = begin \
            .connect(SubroutineNode('expr = get_random_number_expr()')) \
            .connect(OperationNode('previous_op = None'))
        while_cond = subr.connect(ConditionNode('IF iterations > 0'))
        out_cond = while_cond.connect_yes(
            ConditionNode('IF randint from 0-1 == 0'), 'bottom')
        cond = out_cond \
            .connect_yes(OperationNode('op = choose random op from multi_ops'), 'right') \
            .connect(ConditionNode('IF op == previous_op'))
        cond.connect_yes(while_cond, 'right')
        loop_tail = ConditionNode('IF new_expr is None')
        loop_tail.connect_yes(while_cond, 'left')
        loop_tail \
            .connect_no(OperationNode('previous_op = op'), 'bottom') \
            .connect(OperationNode('expr = new_expr')) \
            .connect(OperationNode('iterations -= 1').set_connect_direction('left')) \
            .connect(while_cond)
        cond = cond \
            .connect_no(SubroutineNode('random_expr = get_random_number_expr()'), 'bottom') \
            .connect(ConditionNode('IF randint from 0-1 == 0'))
        cond \
            .connect_yes(OperationNode('new_expr = op(expr, random_expr)').set_connect_direction('left')) \
            .connect(loop_tail)
        cond \
            .connect_no(OperationNode('new_expr = op(random_expr, expr)')) \
            .connect(loop_tail)
        cond = out_cond \
            .connect_no(OperationNode('op = random_choice(single_ops)'), 'bottom') \
            .connect(ConditionNode('IF op == previous_op'))
        cond.connect_yes(while_cond, 'left')
        cond \
            .connect_no(OperationNode('new_expr = op(expr)'), 'bottom') \
            .connect(loop_tail)
        while_cond \
            .connect_no(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN expr'), 'left') \
            .connect(EndNode('END get_q_expr'))
        return begin

    cond = begin \
        .connect(OperationNode('multi_ops = [addition_op, subtraction_op, multiplication_op]')) \
        .connect(OperationNode('single_ops = [division_op, power_op, negate_op, parens_op]')) \
        .connect(SubroutineNode('test_progress = get_test_progress(controller, question_index)')) \
        .connect(ConditionNode('IF difficulty is normal'))
    yes = cond.connect_yes(SubroutineNode(
        'difficulty_progression_factor = round result of map_range(test_progress, 0, 1, 0, 4)')).connect(OperationNode(
            'iterations = randint from (2+difficulty_progression_factor) to (4+difficulty_progression_factor)'))
    no = cond.connect_no(SubroutineNode(
        'difficulty_progression_factor = round result of map_range(test_progress, 0, 1, 0, 15)'), 'left').connect(OperationNode(
            'iterations = randint from (5+difficulty_progression_factor) to (10+difficulty_progression_factor)'))
    subr = SubroutineNode('(expr_str, expr_value, _) = get_q_expr()')
    yes.connect(subr)
    no.connect(subr)
    cond = subr \
        .connect(OperationNode('question = concatenate "Evaluate ", expr_str')) \
        .connect(ConditionNode('IF randint from 0-1 == 0'))
    cond \
        .connect_yes(OperationNode('is_ans_correct = lambda ans: ans == expr_value as string'), 'right') \
        .connect(OperationNode('component = InputQuestion(controller, question, get_integer_error_msg, is_ans_correct, expr_value as string)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN component'))
    while_anchor = cond \
        .connect_no(OperationNode('fake_answer_range = (expr_value but positive) + 15'), 'bottom') \
        .connect(OperationNode('fake_answers = []')) \
        .connect(OperationNode('fake_answer = randint from -fake_answer_range to fake_answer_range'))
    cond = while_anchor.connect(ConditionNode(
        'IF fake_answer == expr_value or fake_answer in fake_answers'))
    cond.connect_yes(while_anchor, 'left')
    cond = cond \
        .connect_no(OperationNode('add fake_answer to fake_answers'), 'bottom') \
        .connect(ConditionNode('IF fake_answers length == 3'))
    cond.connect_no(while_anchor, 'left')
    cond \
        .connect_yes(OperationNode('choices = list with str(expr_value) concatenated with fake_answers')) \
        .connect(OperationNode('shuffle choices')) \
        .connect(OperationNode('correct_choice_index = get index of str(expr_value) in choices')) \
        .connect(OperationNode('component = MultipleChoiceQuestion(controller, question, choices, correct_choice_index)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN component')) \
        .connect(EndNode('END q_bodmas'))

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
        get_random_number_expr_subr(),
        get_q_expr_subr()
    ]


def q_factorise_quadratic_subr():
    begin = StartNode('BEGIN q_factorise_quadratic')

    cond = begin \
        .connect(SubroutineNode('test_progress = get_test_progress(controller, question_index)')) \
        .connect(ConditionNode('IF difficulty is normal'))

    yes = cond \
        .connect_yes(SubroutineNode('max_val = round result of map_range(test_progress, 0, 1, 8, 20)')) \
        .connect(OperationNode('k = 1'))
    no = cond \
        .connect_no(SubroutineNode('max_val = round result of map_range(test_progress, 0, 1, 25, 100)')) \
        .connect(OperationNode('k = randint from 1 to max_val'))

    op = OperationNode('a = randint from -max_val to max_val')
    yes.connect(op)
    no.connect(op)

    cond = op \
        .connect(OperationNode('b = randint from -max_val to max_val')) \
        .connect(OperationNode('x2_coeff = k')) \
        .connect(OperationNode('x1_coeff = k * (a + b)')) \
        .connect(OperationNode('x0_coeff = k * (a * b)')) \
        .connect(OperationNode('poly = make string with x^2 term')) \
        .connect(ConditionNode('IF x1_coeff != 0'))
    cond2 = cond \
        .connect_yes(OperationNode('add x^1 term to poly string')) \
        .connect(ConditionNode('IF x0_coeff != 0'))
    cond.connect_no(cond2)
    op = cond2 \
        .connect_yes(OperationNode('add constant term to poly string')) \
        .connect(OperationNode('question = "Factorise {poly} fully"'))
    cond2.connect_no(op)

    def make_term_subr():
        begin = StartNode('BEGIN make_term')
        cond = begin.connect(ConditionNode('IF n == 0'))
        cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN "x"'))
        cond \
            .connect_no(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN string (x+/-{n})')) \
            .connect(EndNode('END make_term'))
        return begin

    def make_factored_poly_subr():
        begin = StartNode('BEGIN make_factored_poly')
        begin \
            .connect(SubroutineNode('a_term = make_term(a)')) \
            .connect(SubroutineNode('b_term = make_term(b)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN string k*a_term*b_term')) \
            .connect(EndNode('END make_factored_poly'))
        return begin

    op \
        .connect(SubroutineNode('correct_ans = make_factored_poly(a, b)')) \
        .connect(SubroutineNode('wrong_ans_error_range = (a but positive + b but positive) / 2 + 4')) \
        .connect(SubroutineNode('choices = list with correct_ans and three random wrong answers using make_factored_poly and wrong_ans_error_range')) \
        .connect(OperationNode('shuffle choices list')) \
        .connect(OperationNode('correct_choice_index = get index of correct_ans in choices list')) \
        .connect(OperationNode('component = MultipleChoiceQuestion(controller, question, choices, correct_choice_index)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN component')) \
        .connect(EndNode('END q_factorise_quadratic'))

    return [begin, make_term_subr(), make_factored_poly_subr()]


def q_simplify_linear_subr():
    def PolyTerm_subr():
        begin = StartNode('BEGIN class PolyTerm')

        begin \
            .connect(OperationNode('set instance variable value')) \
            .connect(OperationNode('set instance coeff value')) \
            .connect(OperationNode('set instance power value')) \
            .connect(EndNode('END class PolyTerm'))

        return begin

    def poly_to_str_subr():
        begin = StartNode('BEGIN poly_to_str')
        loop_anchor = begin \
            .connect(OperationNode('poly_str = ""')) \
            .connect(OperationNode('FOR each term in terms')) \
            .connect(ConditionNode('No more terms to iterate?'))
        ret = InputOutputNode(InputOutputNode.OUTPUT, 'RETURN poly_str')
        cond = loop_anchor.connect_no(
            ConditionNode('IF term.coeff == 0'), 'bottom')
        cond, _ = cond.connect_no(ConditionNode(
            'IF term.coeff < 0')), cond.connect_yes(loop_anchor, 'right')
        abs_cond = ConditionNode('IF term.coeff is not -1 and is not 1')
        cond2 = cond.connect_yes(ConditionNode('IF poly_str == ""'), 'right')
        cond2.connect_yes(OperationNode('poly_str += "-"')).connect(abs_cond)
        cond2.connect_no(OperationNode('poly_str += " - "')).connect(abs_cond)
        cond2 = cond.connect_no(ConditionNode('IF poly_str != ""'))
        cond2.connect_yes(OperationNode('poly_str += " + "')).connect(abs_cond)
        cond2.connect_no(abs_cond)
        nex_cond = ConditionNode('IF term.power == 0')
        abs_cond.connect_yes(OperationNode(
            'poly_str += absolute value of term.coeff')).connect(nex_cond)
        abs_cond.connect_no(nex_cond)
        cond = nex_cond.connect_no(
            ConditionNode('IF term.power == 1'), 'bottom')
        nex_cond.connect_yes(loop_anchor, 'left')
        cond.connect_no(OperationNode(
            'poly_str += term.variable + "^" + term.power').set_connect_direction('left')).connect(loop_anchor)
        cond.connect_yes(OperationNode(
            'poly_str += term.variable'), 'right').set_connect_direction('top').connect(loop_anchor)
        loop_anchor.connect_yes(OperationNode(
            'Exit loop'), 'right').connect(ret)
        ret.connect(EndNode('END poly_to_str'))
        return begin

    begin = StartNode('BEGIN q_simplify_linear')
    cond = begin \
        .connect(SubroutineNode('test_progress = get_test_progress(controller, question_index)')) \
        .connect(ConditionNode('IF difficulty is normal'))
    op = OperationNode(
        'variable_coeffs = make nested list containing lists of a random number of random integer coefficients for each variable in variables list')
    cond \
        .connect_yes(OperationNode('variables = make list randomly with either "x", "y" or both')) \
        .connect(SubroutineNode('coeff_range = round result of map_range(test_progress, 0, 1, 12, 50)')) \
        .connect(SubroutineNode('max_terms_per_var = round result of map_range(test_progress, 0, 1, 2, 6)')) \
        .connect(op)
    cond \
        .connect_no(OperationNode('variables = list of 3-8 randomly chosen lowercase letters')) \
        .connect(SubroutineNode('coeff_range = round result of map_range(test_progress, 0, 1, 1000, 3000)')) \
        .connect(SubroutineNode('max_temrs_per_var = round result of map_range(test_progress, 0, 1, 5, 12)')) \
        .connect(op)
    subr = op \
        .connect(OperationNode('poly_q_terms = make flat list of PolyTerm(variable, coeff, power=1) for each coefficient of each variable')) \
        .connect(OperationNode('shuffle poly_q_terms')) \
        .connect(OperationNode('poly_q = poly_to_str(poly_q_terms)')) \
        .connect(OperationNode('poly_ans_coeffs = list with nth item being the sum of all the coefficients of nth variable')) \
        .connect(OperationNode('poly_ans_terms = make list of PolyTerm(variable, coeff, power=1) for each variable/coeff in variables/poly_ans_coeffs')) \
        .connect(SubroutineNode('correct_ans = poly_to_str(poly_ans_terms)'))

    def map_term_subr():
        begin = StartNode('BEGIN map_term')
        begin \
            .connect(OperationNode('wrong_range = (absolute value of term.coeff) / 2 + 10')) \
            .connect(OperationNode('term = PolyTerm(variable, coeff=term.coeff + randint from -wrong_range to wrong_range, power=term.power)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN term')) \
            .connect(EndNode('END map_term'))
        return begin

    def make_wrong_ans_subr():
        begin = StartNode('BEGIN make_wrong_ans')
        begin \
            .connect(SubroutineNode('wrong_ans = poly_to_str(map_term(term) for term in poly_ans_terms)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN wrong_ans')) \
            .connect(EndNode('END make_wrong_ans'))
        return begin

    subr \
        .connect(SubroutineNode('choices = list of correct_ans and 3 calls of make_wrong_ans()')) \
        .connect(OperationNode('shuffle choices list')) \
        .connect(OperationNode('correct_choice_index = get index of correct_ans in choices')) \
        .connect(OperationNode('question = "Simplify {poly_q}"')) \
        .connect(OperationNode('component = MultipleChoiceQuestion(controller, question, choices, correct_choice_index)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN component')) \
        .connect(EndNode('END q_simplify_linear'))

    return [begin, PolyTerm_subr(), poly_to_str_subr(), make_wrong_ans_subr(), map_term_subr()]


def q_find_hypot_subr():
    begin = StartNode('BEGIN q_find_hypot')
    cond = begin \
        .connect(OperationNode('pythag_triple_list = stackoverflow magic to generate list of pythagorean triples (a,b,c)')) \
        .connect(SubroutineNode('test_progress = get_test_progress(controller, question_index)')) \
        .connect(ConditionNode('IF difficulty is normal'))
    op = OperationNode('i = randint from 0 to upper_bound')
    cond.connect_yes(OperationNode(
        'upper_bound = round result of map_range(test_progress, 0, 1, 15, 50)')).connect(op)
    cond.connect_no(OperationNode(
        'upper_bound = round result of map_range(test_progress, 0, 1, 500, length of pythag_triple_list - 1)')).connect(op)
    op \
        .connect(OperationNode('a, b, c = pythag_triple_list[i]')) \
        .connect(OperationNode('unit = random item from units list')) \
        .connect(OperationNode('question = "What is the length of the hypotenuse in a right angled triangle with non-hypotenuse sides of length {a}{unit} and {b}{unit}?"')) \
        .connect(OperationNode('d, e, f = pythag_triple_list[index next to i]')) \
        .connect(OperationNode('choices = list of c+unit, d+unit, e+unit, f+unit')) \
        .connect(OperationNode('shuffle choices list')) \
        .connect(OperationNode('correct_choice_index = get index of c+unit in choices list')) \
        .connect(OperationNode('component = MultipleChoiceQuestion(controller, question, choices, correct_choice_index)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN component')) \
        .connect(EndNode('END q_find_hypot'))
    return [begin]


def q_general_geometry_subr():
    begin = StartNode('BEGIN q_general_geometry')

    def rand_progressive_subr():
        begin = StartNode('BEGIN rand_progressive')
        subr = SubroutineNode(
            'max = round result of map_range(test_progress, 0, 1, min_upper + (max_upper - min_upper) / 5, max_upper * difficulty_factor)')
        cond = begin.connect(ConditionNode('IF difficulty == normal'))
        cond.connect_yes(OperationNode('difficulty_factor = 1')).connect(subr)
        cond.connect_no(OperationNode('difficulty_factor = 100')).connect(subr)
        subr \
            .connect(OperationNode('rand_num = randint from min_upper to max')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN rand_num')) \
            .connect(EndNode('END rand_progressive'))
        return begin

    def circle_area_from_radius_subr():
        begin = StartNode('BEGIN circle_area_from_radius')
        begin \
            .connect(SubroutineNode('radius = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the area of a circle with radius {radius}{unit}')) \
            .connect(OperationNode('ans = pi * radius ** 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_area_from_radius'))
        return begin

    def circle_area_from_diameter_subr():
        begin = StartNode('BEGIN circle_area_from_diameter')
        begin \
            .connect(SubroutineNode('diameter = rand_progressive(5, 200)')) \
            .connect(OperationNode('question = string What is the area of a circle with diameter {diameter}{unit}')) \
            .connect(OperationNode('ans = pi * (diameter / 2) ** 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_area_from_diameter'))
        return begin

    def circle_area_from_circumference_subr():
        begin = StartNode('BEGIN circle_area_from_circumference')
        begin \
            .connect(SubroutineNode('circumference = rand_progressive(5, 600)')) \
            .connect(OperationNode('question = string What is the area of a circle with circumference {circumference}{unit}')) \
            .connect(OperationNode('ans = pi * radius ** 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_area_from_circumference'))
        return begin

    def circle_circumference_from_radius_subr():
        begin = StartNode('BEGIN circle_circumference_from_radius')
        begin \
            .connect(SubroutineNode('radius = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the circumference of a circle with radius {radius}{unit}')) \
            .connect(OperationNode('ans = 2 * pi * radius')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_circumference_from_radius'))
        return begin

    def circle_circumference_from_diameter_subr():
        begin = StartNode('BEGIN circle_circumference_from_diameter')
        begin \
            .connect(SubroutineNode('diameter = rand_progressive(5, 200)')) \
            .connect(OperationNode('question = string What is the circumference of a circle with diameter {diameter}{unit}')) \
            .connect(OperationNode('ans = 2 * pi * (diameter / 2)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_circumference_from_diameter'))
        return begin

    def circle_circumference_from_area_subr():
        begin = StartNode('BEGIN circle_circumference_from_area')
        begin \
            .connect(SubroutineNode('area = rand_progressive(5, 10000)')) \
            .connect(OperationNode('radius = sqrt of (area / pi)')) \
            .connect(OperationNode('question = string What is the circumference of a circle with area {area}{unit}')) \
            .connect(OperationNode('ans = 2 * pi * radius')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_circumference_from_area'))
        return begin

    def circle_radius_from_diameter_subr():
        begin = StartNode('BEGIN circle_radius_from_diameter')
        begin \
            .connect(SubroutineNode('diameter = rand_progressive(5, 200)')) \
            .connect(OperationNode('question = string What is the radius of a circle with diameter {diameter}{unit}')) \
            .connect(OperationNode('ans = diameter / 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_radius_from_diameter'))
        return begin

    def circle_radius_from_circumference_subr():
        begin = StartNode('BEGIN circle_radius_from_circumference')
        begin \
            .connect(SubroutineNode('circumference = rand_progressive(5, 600)')) \
            .connect(OperationNode('question = string What is the radius of a circle with circumference {circumference}{unit}')) \
            .connect(OperationNode('ans = circumference / 2 / pi')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_radius_from_circumference'))
        return begin

    def circle_radius_from_area_subr():
        begin = StartNode('BEGIN circle_radius_from_area')
        begin \
            .connect(SubroutineNode('area = rand_progressive(5, 10000)')) \
            .connect(OperationNode('question = string What is the radius of a circle with area {area}{unit}')) \
            .connect(OperationNode('ans = sqrt of (area / pi)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_radius_from_area'))
        return begin

    def circle_diameter_from_radius_subr():
        begin = StartNode('BEGIN circle_diameter_from_radius')
        begin \
            .connect(SubroutineNode('radius = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the diameter of a circle with radius {radius}{unit}')) \
            .connect(OperationNode('ans = radius * 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_diameter_from_radius'))
        return begin

    def circle_diameter_from_circumference_subr():
        begin = StartNode('BEGIN circle_diameter_from_circumference')
        begin \
            .connect(SubroutineNode('circumference = rand_progressive(5, 600)')) \
            .connect(OperationNode('question = string What is the diameter of a circle with circumference {circumference}{unit}')) \
            .connect(OperationNode('ans = circumference / pi')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_diameter_from_circumference'))
        return begin

    def circle_diameter_from_area_subr():
        begin = StartNode('BEGIN circle_diameter_from_area')
        begin \
            .connect(SubroutineNode('area = rand_progressive(5, 10000)')) \
            .connect(OperationNode('question = string What is the diameter of a circle with area {area}{unit}')) \
            .connect(OperationNode('ans = (sqrt of (area / pi)) * 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END circle_diameter_from_area'))
        return begin

    def square_perimeter_from_side_length_subr():
        begin = StartNode('BEGIN square_perimeter_from_side_length')
        begin \
            .connect(SubroutineNode('side_length = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the perimeter of a square with side length {side_length}{unit}')) \
            .connect(OperationNode('ans = side_length * 4')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END square_perimeter_from_side_length'))
        return begin

    def square_perimeter_from_area_subr():
        begin = StartNode('BEGIN square_perimeter_from_area')
        begin \
            .connect(SubroutineNode('area = rand_progressive(5, 10000)')) \
            .connect(OperationNode('question = string What is the perimeter of a square with side length {area}{unit}')) \
            .connect(OperationNode('ans = (sqrt of area) * 4')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END square_perimeter_from_area'))
        return begin

    def square_side_length_from_perimeter_subr():
        begin = StartNode('BEGIN square_side_length_from_perimeter')
        begin \
            .connect(SubroutineNode('perimeter = rand_progressive(5, 400)')) \
            .connect(OperationNode('question = string What is the side length of a square with perimeter {perimeter}{unit}')) \
            .connect(OperationNode('ans = perimeter / 4')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END square_side_length_from_perimeter'))
        return begin

    def square_side_length_from_area_subr():
        begin = StartNode('BEGIN square_side_length_from_area')
        begin \
            .connect(SubroutineNode('area = rand_progressive(5, 100000)')) \
            .connect(OperationNode('question = string What is the side length of a square with area {area}{unit}')) \
            .connect(OperationNode('ans = sqrt of area')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END square_side_length_from_area'))
        return begin

    def square_area_from_side_length_subr():
        begin = StartNode('BEGIN square_area_from_side_length')
        begin \
            .connect(SubroutineNode('side_length = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the area of a square with side length {side_length}{unit}')) \
            .connect(OperationNode('ans = side_length ** 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END square_area_from_side_length'))
        return begin

    def square_area_from_perimeter_subr():
        begin = StartNode('BEGIN square_area_from_perimeter')
        begin \
            .connect(SubroutineNode('perimeter = rand_progressive(5, 400)')) \
            .connect(OperationNode('question = string What is the area of a square with side length {perimeter}{unit}')) \
            .connect(OperationNode('ans = (perimeter / 4) ** 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END square_area_from_perimeter'))
        return begin

    def rectangle_area_from_side_lengths_subr():
        begin = StartNode('BEGIN rectangle_area_from_side_lengths')
        begin \
            .connect(SubroutineNode('a = rand_progressive(5, 100)')) \
            .connect(SubroutineNode('b = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the area of a rectangle with side lengths {a}{unit} and {b}{unit}')) \
            .connect(OperationNode('ans = a * b')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END rectangle_area_from_side_lengths'))
        return begin

    def rectangle_perimeter_from_side_lengths_subr():
        begin = StartNode('BEGIN rectangle_perimeter_from_side_lengths')
        begin \
            .connect(SubroutineNode('a = rand_progressive(5, 100)')) \
            .connect(SubroutineNode('b = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the perimeter of a rectangle with side lengths {a}{unit} and {b}{unit}')) \
            .connect(OperationNode('ans = 2 * (a + b)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END rectangle_perimeter_from_side_lengths'))
        return begin

    def triangle_area_from_base_height_subr():
        begin = StartNode('BEGIN triangle_area_from_base_height')
        begin \
            .connect(SubroutineNode('base = rand_progressive(5, 100)')) \
            .connect(SubroutineNode('height = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the area of a triangle with base {base}{unit} and height {height}{unit}')) \
            .connect(OperationNode('ans = base * height / 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END triangle_area_from_base_height'))
        return begin

    def trapezoid_area_from_top_bottom_height_subr():
        begin = StartNode('BEGIN trapezoid_area_from_top_bottom_height')
        begin \
            .connect(SubroutineNode('top = rand_progressive(5, 100)')) \
            .connect(SubroutineNode('bottom = rand_progressive(5, 100)')) \
            .connect(SubroutineNode('height = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the area of a trapezoid with bottom side {bottom}{unit}, top side {top}{unit} and height {height}{unit}')) \
            .connect(OperationNode('ans = (bottom + top) / 2 * height')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END trapezoid_area_from_top_bottom_height'))
        return begin

    def rhombus_area_from_diagonals_subr():
        begin = StartNode('BEGIN rhombus_area_from_diagonals')
        begin \
            .connect(SubroutineNode('p = rand_progressive(5, 100)')) \
            .connect(SubroutineNode('q = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the area of a rhombus with diagonals {p}{unit} and {q}{unit}')) \
            .connect(OperationNode('ans = p * q / 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END rhombus_area_from_diagonals'))
        return begin

    def kite_area_from_diagonals_subr():
        begin = StartNode('BEGIN kite_area_from_diagonals')
        begin \
            .connect(SubroutineNode('p = rand_progressive(5, 100)')) \
            .connect(SubroutineNode('q = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the area of a kite with diagonals {p}{unit} and {q}{unit}')) \
            .connect(OperationNode('ans = p * q / 2')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END kite_area_from_diagonals'))
        return begin

    def hypot_from_ab_subr():
        begin = StartNode('BEGIN hypot_from_ab')
        begin \
            .connect(SubroutineNode('a = rand_progressive(5, 100)')) \
            .connect(SubroutineNode('b = rand_progressive(5, 100)')) \
            .connect(OperationNode('question = string What is the length of the hypotenuse in a right angled triangle with non-hypotenuse sides of length {a}{unit} and {b}{unit}')) \
            .connect(OperationNode('ans = sqrt of (a ** 2 + b ** 2)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END hypot_from_ab'))
        return begin

    def b_from_hypot_a_subr():
        begin = StartNode('BEGIN b_from_hypot_a')
        begin \
            .connect(SubroutineNode('a = rand_progressive(5, 100)')) \
            .connect(SubroutineNode('hypot = rand_progressive(a + 1, a * 2)')) \
            .connect(OperationNode('question = string What is the length of the other non-hypotenuse side in a right angled triangle with hypotenuse of length {hypot}{unit} and non-hypotenuse side of length {a}{unit}')) \
            .connect(OperationNode('ans = sqrt of (hypot ** 2 - a ** 2)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question, ans')) \
            .connect(EndNode('END b_from_hypot_a'))
        return begin

    cond = begin \
        .connect(SubroutineNode('test_progress = get_test_progress(controller, question_index)')) \
        .connect(OperationNode('q_factories = list of all general geometry question factories')) \
        .connect(OperationNode('q_factory = choose random item from q_factories list')) \
        .connect(OperationNode('unit = random choice from units list')) \
        .connect(SubroutineNode('(question, exact_ans) = q_factory(unit)')) \
        .connect(ConditionNode('IF exact_ans is integer'))

    def roundTraditional_subr():
        begin = StartNode('BEGIN roundTraditional')
        begin \
            .connect(OperationNode('result = stack overflow magic to round val to given number of digits (decimal points)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN result')) \
            .connect(EndNode('END roundTraditional'))
        return begin

    op = SubroutineNode(
        'correct_ans = roundTraditional(exact_ans, dp) as float')
    cond.connect_yes(OperationNode('dp = 0')).connect(op)
    cond.connect_no(OperationNode('dp = randint from 0 to 4')).connect(op)
    op = op.connect(OperationNode(
        'add dp information (round to nearest {dp} dp) to end of question string'))

    def num_to_str_subr():
        begin = StartNode('BEGIN num_to_str')
        begin \
            .connect(OperationNode('result = format num to {dp} decimal places')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN result')) \
            .connect(EndNode('END num_to_str'))
        return begin

    def get_input_error_msg_subr():
        begin = StartNode('BEGIN get_input_error_msg')
        cond = begin \
            .connect(SubroutineNode('float_err = get_float_error_msg(text)')) \
            .connect(ConditionNode('IF float_err'))
        cond.connect_yes(InputOutputNode(
            InputOutputNode.OUTPUT, 'RETURN float_err'))
        cond = cond \
            .connect_no(OperationNode('num = text as float')) \
            .connect(ConditionNode('IF num < 0'))
        cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT,
                                         'RETURN "Please enter a positive integer."'))
        cond \
            .connect_no(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN None')) \
            .connect(EndNode('END get_input_error_msg'))
        return begin

    def input_q_is_ans_correct_subr():
        begin = StartNode('BEGIN input_q_is_ans_correct')
        begin \
            .connect(SubroutineNode('correct_ans_as_str = num_to_str(correct_ans)')) \
            .connect(OperationNode('result = num == correct_ans_as_str')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN result')) \
            .connect(EndNode('END input_q_is_ans_correct'))
        return begin

    cond = op.connect(ConditionNode('IF randint from 0-1 is 0'))
    cond \
        .connect_yes(OperationNode('component = InputQuestion(controller,\n question,\n get_input_error_msg,\n input_q_is_ans_correct,\n correct_ans)'), 'right') \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN component'))
    while_anchor = cond \
        .connect_no(OperationNode('fake_answer_min = round (correct_ans / 3) + 1'), 'bottom') \
        .connect(OperationNode('fake_answer_max = round (correct_ans * 3) + 1')) \
        .connect(OperationNode('fake_answers = []')) \
        .connect(ConditionNode('IF correct_ans is integer'))
    cond = ConditionNode(
        'IF fake_answer == correct_ans or fake_answer in fake_answers list')
    while_anchor \
        .connect_yes(OperationNode('fake_answer = randint from fake_answer_min to fake_answer_max')) \
        .connect(cond)
    while_anchor \
        .connect_no(SubroutineNode('rounded_correct_ans = num_to_str(correct_ans)'), 'left') \
        .connect(OperationNode('num_zeros = length of rounded_correct_ans - length of rounded_correct_ans without trailing zeros')) \
        .connect(OperationNode('fake_raw = randfloat from fake_answer_min to fake_answer_max')) \
        .connect(SubroutineNode('fake_answer = roundTraditional(fake_raw, dp - num_zeros)').set_connect_direction('right')) \
        .connect(cond)
    cond.connect_yes(while_anchor, 'right')
    cond = cond \
        .connect_no(OperationNode('add fake_answer to fake_answers list'), 'bottom') \
        .connect(ConditionNode('IF length of fake_answers list is 3'))
    cond.connect_no(while_anchor)
    cond \
        .connect_yes(OperationNode('choices = list with correct_ans+unit and all the fake_answers but with unit appended at end')) \
        .connect(OperationNode('shuffle choices list')) \
        .connect(OperationNode('correct_choice_index = get index of correct ans in choices list')) \
        .connect(OperationNode('component = MultipleChoiceComponent(controller, question, choices, correct_choice_index)')) \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN component')) \
        .connect(EndNode('END q_general_geometry'))

    return [
        begin,
        rand_progressive_subr(),
        circle_area_from_radius_subr(),
        circle_area_from_diameter_subr(),
        circle_area_from_circumference_subr(),
        circle_circumference_from_radius_subr(),
        circle_circumference_from_diameter_subr(),
        circle_circumference_from_area_subr(),
        circle_radius_from_diameter_subr(),
        circle_radius_from_circumference_subr(),
        circle_radius_from_area_subr(),
        circle_diameter_from_radius_subr(),
        circle_diameter_from_circumference_subr(),
        circle_diameter_from_area_subr(),
        square_perimeter_from_side_length_subr(),
        square_perimeter_from_area_subr(),
        square_side_length_from_perimeter_subr(),
        square_side_length_from_area_subr(),
        square_area_from_side_length_subr(),
        square_area_from_perimeter_subr(),
        rectangle_area_from_side_lengths_subr(),
        rectangle_perimeter_from_side_lengths_subr(),
        triangle_area_from_base_height_subr(),
        trapezoid_area_from_top_bottom_height_subr(),
        rhombus_area_from_diagonals_subr(),
        kite_area_from_diagonals_subr(),
        hypot_from_ab_subr(),
        b_from_hypot_a_subr(),
        roundTraditional_subr(),
        num_to_str_subr(),
        get_input_error_msg_subr(),
        input_q_is_ans_correct_subr()
    ]


def make_questions_subr():
    begin = StartNode('BEGIN make_questions')
    begin.connect(OperationNode('possible_questions = []'))
    cond = begin.connect(ConditionNode('IF number theory in content'))
    nex_cond = cond.connect_no(ConditionNode('IF algebra in content'))
    cond.connect_yes(OperationNode(
        'add q_bodmas to possible_questions list')).connect(nex_cond)
    cond = nex_cond.connect_no(ConditionNode('IF geometry in content'))
    nex_cond.connect_yes(OperationNode(
        'add q_factorise_quadratic to possible_questions list')).connect(OperationNode('add q_simplify_linear to possible_questions list')).connect(cond)
    subr = cond.connect_no(SubroutineNode(
        'result = list with length {question_count}, i\'th item = make_question(i)'))
    cond.connect_no(subr)
    cond.connect_yes(OperationNode(
        'add q_find_hypot to possible questions list')).connect(OperationNode('add q_general_geometry to possible questions list')).connect(subr)
    subr \
        .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN result')) \
        .connect(EndNode('END make_questions'))

    def make_question_subr():
        begin = StartNode('BEGIN make_question')
        begin \
            .connect(OperationNode('make_question_component = random choice from possible_questions')) \
            .connect(SubroutineNode('question_component = make_question_component(controller, question_index)')) \
            .connect(OperationNode('question = TestQuestion(question_component, answer_state=not answered)')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question')) \
            .connect(EndNode('END make_question'))
        return begin

    return [begin, make_question_subr()]


def finish_subr():
    begin = StartNode('BEGIN FinishScreen')

    def format_time_subr():
        begin = StartNode('BEGIN format_time')
        begin \
            .connect(SubroutineNode('(m, s) = divmod(round time, 60)')) \
            .connect(SubroutineNode('(h, m) = divmod(m, 60)')) \
            .connect(OperationNode('result = "Hours: {h}, Minutes: {m}, Seconds: {s}"')) \
            .connect(InputOutputNode(InputOutputNode.OUTPUT, 'RETURN result')) \
            .connect(EndNode('END format_time'))
        return begin

    def on_back_click_subr():
        begin = StartNode('BEGIN on_back_click')
        begin \
            .connect(OperationNode('test = Test(start_time, questions, question_index=length of questions - 1)')) \
            .connect(OperationNode('new_state = PlayingScreenState(session, test)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_back_click'))
        return begin

    def on_help_click_subr():
        begin = StartNode('BEGIN on_help_click')
        begin \
            .connect(OperationNode('new_state = HelpScreenState(session, previous_state=state)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_help_click'))
        return begin

    def on_menu_click_subr():
        begin = StartNode('BEGIN on_menu_click')
        begin \
            .connect(OperationNode('new_state = MenuScreenState(session)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_menu_click'))
        return begin

    def on_retry_test_click_subr():
        begin = StartNode('BEGIN on_retry_test_click')
        begin \
            .connect(SubroutineNode('start_time = get_cur_time()')) \
            .connect(OperationNode('new_questions = map questions list and change each question\'s answer state to not answered')) \
            .connect(OperationNode('test = Test(start_time, new_questions, question_index=0)')) \
            .connect(OperationNode('new_state = PlayingScreenState(session, test)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_retry_test_click'))
        return begin

    def map_question_subr():
        begin = StartNode('BEGIN map_question')
        cond = begin.connect(ConditionNode(
            'IF question is answered incorrect'))
        cond.connect_yes(OperationNode('question = TestQuestion(question_component, answer_state=not answered)')).connect(
            InputOutputNode(InputOutputNode.OUTPUT, 'RETURN question'))
        cond.connect_no(InputOutputNode(InputOutputNode.OUTPUT,
                                        'RETURN question')).connect(EndNode('END map_question'))
        return begin

    def on_retry_incorrect_questions_click_subr():
        begin = StartNode('BEGIN on_retry_incorrect_questions_click')
        loop_anchor = begin \
            .connect(OperationNode('FOR i, question in questions')) \
            .connect(ConditionNode('No more questions to iterate?'))
        cond = loop_anchor.connect_no(ConditionNode(
            'IF question is answered incorrect'))
        loop_tail = SubroutineNode(
            'new_questions = [map_question(question) for question in questions]')
        cond.connect_yes(
            OperationNode('first_incorrect_question_index = i')).connect(loop_tail)
        cond.connect_no(loop_anchor)
        loop_anchor.connect_yes(OperationNode('Exit loop')).connect(loop_tail)
        loop_tail \
            .connect(OperationNode('test = Test(start_time, new_questions, first_incorrect_question_index)')) \
            .connect(OperationNode('new_state = PlayingScreenState(session, test)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_retry_incorrect_questions_click'))
        return begin

    begin \
        .connect(OperationNode('questions_right = sum number questions in questions list that are answered correct')) \
        .connect(SubroutineNode('current_time = get_cur_time()')) \
        .connect(OperationNode('time_played = current_time - start_time')) \
        .connect(SubroutineNode('time_played_formatted = format_time(time_played)')) \
        .connect(OperationNode('UI set finish screen ui')) \
        .connect(OperationNode('UI on back button click call on_back_click')) \
        .connect(OperationNode('UI on help button click call on_help_click')) \
        .connect(OperationNode('UI on menu button click call on_menu_click')) \
        .connect(OperationNode('UI on retry test button click call on_retry_test_click')) \
        .connect(OperationNode('UI on retry incorrect questions button click call on_retry_incorrect_questions_click')) \
        .connect(EndNode('END FinishScreen'))

    return [begin, format_time_subr(), on_back_click_subr(), on_help_click_subr(), on_menu_click_subr(), on_retry_test_click_subr(), on_retry_incorrect_questions_click_subr(), map_question_subr()]


def playing_subr():
    begin = StartNode('BEGIN PlayingScreen')
    cond = begin.connect(ConditionNode(
        'IF question_index == length of questions list'))
    cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT,
                                     'RETURN FinishScreen(controller)'), 'right')

    def update_question_answer_state_subr():
        begin = StartNode('BEGIN update_question_answer_state')
        begin \
            .connect(OperationNode('new_current_question = TestQuestion(current_question_component, answer_state)')) \
            .connect(OperationNode('new_questions = make copy of test questions list')) \
            .connect(OperationNode('new_questions[question_index] = new_current_question')) \
            .connect(OperationNode('test = Test(start_time, new_questions, question_index)')) \
            .connect(OperationNode('new_state = PlayingScreenState(session, test)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END update_question_answer_state'))
        return begin

    def on_back_click_subr():
        begin = StartNode('BEGIN on_back_click')
        begin \
            .connect(OperationNode('test = Test(start_time, questions, question_index=question_index-1)')) \
            .connect(OperationNode('new_state = PlayingScreenState(session, test)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_back_click'))
        return begin

    def on_next_click_subr():
        begin = StartNode('BEGIN on_next_click')
        begin \
            .connect(OperationNode('test = Test(start_time, questions, question_index=question_index+1)')) \
            .connect(OperationNode('new_state = PlayingScreenState(session, test)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_next_click'))
        return begin

    def on_help_click_subr():
        begin = StartNode('BEGIN on_help_click')
        begin \
            .connect(OperationNode('new_state = HelpScreenState(session, previous_state=state)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_help_click'))
        return begin

    def on_menu_click_subr():
        begin = StartNode('BEGIN on_menu_click')
        begin \
            .connect(OperationNode('new_state = MenuScreenState(session)')) \
            .connect(OperationNode('UI set state new_state')) \
            .connect(EndNode('END on_menu_click'))
        return begin

    cond \
        .connect_no(OperationNode('current_question = questions[question_index]')) \
        .connect(SubroutineNode('body = current_question_component.render(update_question_answer_state)')) \
        .connect(OperationNode('UI set playing screen ui with body')) \
        .connect(OperationNode('UI on back button click call on_back_click')) \
        .connect(OperationNode('UI on next button click call on_next_click')) \
        .connect(OperationNode('UI on help button click call on_help_click')) \
        .connect(OperationNode('UI on menu button click call on_menu_click')) \
        .connect(EndNode('END PlayingScreen'))

    return [
        begin,
        update_question_answer_state_subr(),
        on_back_click_subr(),
        on_next_click_subr(),
        on_help_click_subr(),
        on_menu_click_subr()
    ]


def root_subr():
    begin = StartNode('BEGIN RootScreen')
    cond = begin.connect(ConditionNode(
        'IF state screen type is set username screen'))
    cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT,
                                     'RETURN SetUsernameScreen(controller)'))
    cond = cond.connect_no(ConditionNode(
        'IF state screen type is menu screen'))
    cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT,
                                     'RETURN MenuScreen(controller)'))
    cond = cond.connect_no(ConditionNode(
        'IF state screen type is help screen'))
    cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT,
                                     'RETURN HelpScreen(controller)'))
    cond = cond.connect_no(ConditionNode(
        'IF state screen type is settings screen'))
    cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT,
                                     'RETURN SettingsScreen(controller)'))
    cond = cond.connect_no(ConditionNode(
        'IF state screen type is playing screen'))
    cond.connect_yes(InputOutputNode(InputOutputNode.OUTPUT,
                                     'RETURN PlayingScreen(controller)')).connect(EndNode('END RootScreen'))
    return [begin]


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
        q_bodmas_subr(),
        q_factorise_quadratic_subr(),
        q_simplify_linear_subr(),
        q_find_hypot_subr(),
        q_general_geometry_subr(),
        make_questions_subr(),
        finish_subr(),
        playing_subr(),
        root_subr()
    )
]))
