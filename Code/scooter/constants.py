BROKER = "mqtt20.iik.ntnu.no"
PORT = 1883

TEAM = "team11"


BAR = [
    (0, 0),
    (1, 0),
    (2, 0),
    (3, 0),
    (4, 0),
    (5, 0),
    (6, 0),
    (7, 0),
    (0, 1),
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 1),
    (5, 1),
    (6, 1),
    (7, 1),
]

CHECK_MARK = [(1, 5), (2, 6), (3, 5), (4, 4), (5, 3)]

X_MARK = [
    (1, 3),
    (2, 4),
    (3, 5),
    (4, 6),
    (5, 7),
    (1, 7),
    (2, 6),
    (4, 4),
    (5, 3),
]

CHARGING_MARK = [
    (1, 3),
    (2, 3),
    (3, 3),
    (4, 3),
    (5, 3),
    (6, 3),
    (1, 4),
    (1, 5),
    (1, 6),
    (6, 4),
    (6, 5),
    (6, 6),
    (2, 6),
    (3, 6),
    (4, 6),
    (5, 6),
]

CHARGING_ANIMATION = [
    [(2, 4), (2, 5)],
    [(3, 4), (3, 5)],
    [(4, 4), (4, 5)],
    [(5, 4), (5, 5)],
]


def seven_segment_display_list(number, x, y):
    # Convert an integer to a 7-segment display representation
    # in area 3x5 starting from top left => (0,3)
    # and return it as a list

    # Define the segments for each digit
    #    —0—
    #  |     |
    #  1     2
    #  |     |
    #    —3—
    #  |     |
    #  4     5
    #  |     |
    #    —6—

    segments = {
        0: [1, 1, 1, 0, 1, 1, 1],
        1: [0, 0, 1, 0, 0, 1, 0],
        2: [1, 0, 1, 1, 1, 0, 1],
        3: [1, 0, 1, 1, 0, 1, 1],
        4: [0, 1, 1, 1, 0, 1, 0],
        5: [1, 1, 0, 1, 0, 1, 1],
        6: [1, 1, 0, 1, 1, 1, 1],
        7: [1, 0, 1, 0, 0, 0, 0],
        8: [1, 1, 1, 1, 1, 1, 1],
        9: [1, 1, 1, 1, 0, 1, 1],
    }

    # Convert the number to a string to handle each digit
    display_list = []

    seg = segments[number]

    # Create the pixel coordinates for the segments
    if seg[0]:
        display_list.append((x, y))
        display_list.append((x + 1, y))
        display_list.append((x + 2, y))
    if seg[1]:
        display_list.append((x, y))
        display_list.append((x, y + 1))
        display_list.append((x, y + 2))
    if seg[2]:
        display_list.append((x + 2, y))
        display_list.append((x + 2, y + 1))
        display_list.append((x + 2, y + 2))
    if seg[3]:
        display_list.append((x, y + 2))
        display_list.append((x + 1, y + 2))
        display_list.append((x + 2, y + 2))
    if seg[4]:
        display_list.append((x, y + 2))
        display_list.append((x, y + 3))
        display_list.append((x, y + 4))
    if seg[5]:
        display_list.append((x + 2, y + 2))
        display_list.append((x + 2, y + 3))
        display_list.append((x + 2, y + 4))
    if seg[6]:
        display_list.append((x, y + 4))
        display_list.append((x + 1, y + 4))
        display_list.append((x + 2, y + 4))

    return display_list
