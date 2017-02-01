class Palete:
    colors = []

    def __init__(self):
        pass

    def get_size(self):
        return len(self.colors)

    def get_colors(self):
        return self.colors

    def get_color(self, index):
        return self.colors[index]

    def add_color(self, color):
        self.colors.append(color)


class Color:
    def __init__(self, r, g, b):
        #print(r,g,b)
        super().__init__()
        self.r = r
        self.g = g
        self.b = b

    def rgb(self):
        return (self.r, self.g, self.b)
