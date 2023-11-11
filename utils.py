def color_inverse(color):
    r,g,b = color
    return 255-r,255-g,255-b

def index_2d(data,val):
    for idx,lst in enumerate(data):
        if val in lst:
            return idx, lst.index(val)

def index_all_2d(data,val):
    res = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] == val:
                res.append((i,j))
    return res
