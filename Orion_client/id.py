## -*- Encoding: UTF-8 -*-

prochainid = 0


def get_prochain_id():
    global prochainid
    prochainid += 1
    return f'id_{prochainid}'


if __name__ == '__main__':
    test()