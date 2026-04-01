class Inventory:
    def __init__(self):
        self.stock = {
            "Resistor": 0,
            "Capacitor": 0,
            "Diode": 0,
            "Transistor": 0,
            "Wire": 0,
            "Tactical": 0,
        }

    def count(self, name):
        return self.stock.get(name, 0)

    def has(self, name):
        return self.count(name) > 0

    def spend(self, name):
        if not self.has(name):
            return False
        self.stock[name] -= 1
        return True

    def earn(self, name, amount):
        self.stock[name] = self.stock.get(name, 0) + amount

    def give_starter(self, starter):
        for name, count in starter.items():
            self.earn(name, count)
