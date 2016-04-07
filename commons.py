

def parser(x, y):
    try:
        x = int(x)
        y = int(y)
        if x not in range(9):
            x, y = -1, -1
        if y not in range(9):
            x, y = -1, -1
    except ValueError:
        x, y = -1, -1
    return x, y
