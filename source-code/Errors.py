ERRORS: dict = {
    0: 'Incorrect amount of arguments',
    1: 'Incorrect values of arguments',
    2: 'Too high exploit level',
    3: 'Max amount of exploits reached',
    4: 'Purchase failed',
    5: 'Failed to add the offer',
    6: 'You are not registered yet',
    7: 'Failed to join to the squad',
}

EXPLANATIONS: dict = {
    0: 'Take a look at \'help\' cmd here',
    1: 'Exploit lvl shouldn\'t be grather than your AI lvl',
    2: 'Max lvl reached',
    3: 'Max amount of exploits reached',
    4: 'Transaction failed',
    5: 'No exploit with that id',
    6: 'Max amount of members reached',
}


def error(error_id: int, explanation_id: int|None=None) -> str:
    if explanation_id == None:
        return f'{ERRORS[error_id]}!'
    
    return f'{ERRORS[error_id]}! {EXPLANATIONS[explanation_id]}.'
