"""
Generates a color based off of a given string
"""
def generate_color(input_string,default_r,default_g,default_b):
    ascii_values = [ord(c) for c in input_string]
    ascii_concat = None
    ascii_concat_reverse = None
    for a in ascii_values:
        if ascii_concat:
            ascii_concat = ascii_concat + str(a)
        else:
            ascii_concat = str(a)
    for a in ascii_values:
        if ascii_concat_reverse:
            ascii_concat_reverse = str(a) + ascii_concat_reverse
        else:
            ascii_concat_reverse = str(a)
    ascii_concat = int(ascii_concat) + int(ascii_concat_reverse)
    ret1 = ascii_concat
    ret2 = ascii_concat_reverse
    #ascii_concat = int(float("." + ascii_concat) * 20)
    #ascii_concat_reverse = int(float("." + ascii_concat_reverse) * 20)
    new_r = int(default_r)
    new_g = int(default_g)
    new_b = int(default_b)


    if ascii_concat % 12 == 0:
        new_r = int(ascii_concat)
    elif ascii_concat % 12 == 1:
        new_g = int(ascii_concat)
    elif ascii_concat % 12 == 2:
        new_b = int(ascii_concat)
    elif ascii_concat % 12 == 3:
        new_r = int(ascii_concat)
        new_g = int(ascii_concat)
    elif ascii_concat % 12 == 4:
        new_r = int(ascii_concat)
        new_b = int(ascii_concat)
    elif ascii_concat % 12 == 5:
        new_g = int(ascii_concat)
        new_b = int(ascii_concat)
    elif ascii_concat % 12 == 6:
        new_r = int(ascii_concat_reverse)
    elif ascii_concat % 12 == 7:
        new_g = int(ascii_concat_reverse)
    elif ascii_concat % 12 == 8:
        new_b = int(ascii_concat_reverse)
    elif ascii_concat % 12 == 9:
        new_r = int(ascii_concat_reverse)
        new_g = int(ascii_concat_reverse)
    elif ascii_concat % 12 == 10:
        new_r = int(ascii_concat_reverse)
        new_b = int(ascii_concat_reverse)
    elif ascii_concat % 12 == 11:
        new_g = int(ascii_concat_reverse)
        new_b = int(ascii_concat_reverse)

    new_r = int(new_r % 230)
    new_g = int(new_g % 230)
    new_b = int(new_b % 230)
    if new_r < 128:
        new_r += 64
    if new_g < 128:
        new_g += 64
    if new_b < 128:
        new_b += 64

    return (new_r,new_g,new_b)

"""Generates hex color for given RGB and makes it lighter"""
def generate_text(input_string,default_r,default_g,default_b):
    new_r,new_g,new_b = generate_color(input_string,default_r,default_g,default_b)
    luminance = 1 - ((.299 * new_r )+ (.587 * new_g) + (.114 * new_b))/255
    #print(luminance)
    if luminance < .5:
        return "#000000"
    else:
        return "#ffffff"

def rgb_to_hex(r,g,b):
    return '#%02x%02x%02x' % (r,g,b)
