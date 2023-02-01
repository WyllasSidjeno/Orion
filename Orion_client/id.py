""" Module de géneration d'identifiant unique"""

# -*- Encoding: UTF-8 -*-

prochainid = 0
""":type: int"""


def get_prochain_id():
    """Recupere le prochain id a utiliser.

    :return: L'ID a utiliser.
    :rtype: str
    """
    global prochainid
    prochainid += 1
    return f'id_{prochainid}'


#if __name__ == '__main__':
#   test()
# Removed main because it was not used and it was not working and
# it was not needed for the game to work. Plus test() was not defined.