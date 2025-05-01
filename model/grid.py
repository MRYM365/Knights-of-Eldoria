class Grid:
    def __init__(self, size=20):
        self.size = size
        self.cells = [[None for _ in range(size)] for _ in range(size)]