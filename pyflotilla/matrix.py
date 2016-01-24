from .module import Module


class Matrix(Module):
    pixels = [0] * 8
    light = 40

    def set_pixel(self, x, y, state):
        if state:
            self.pixels[7-x] |= (1 << y)
        else:
            self.pixels[7-x] &= ~(1 << y)

        self.send()