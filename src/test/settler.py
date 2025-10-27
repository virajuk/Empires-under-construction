class Settler:

    def __init__(self, name):
        self.name = name

    def locate(self):
        self.coordinates = (100, 260)

    def wear_clothes(self):
        self.clothes = "Trousers and Shirt"

class WoodSettler(Settler):
    
    def init_as_wood_settler(self):
        self.wood_carried = 0

    def wear_clothes(self):
        self.clothes = "Only Trousers"

    def bear_tools(self):
        self.tools = "Axe"
