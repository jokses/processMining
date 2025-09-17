#s072446 Joachim Knudsen

class PetriNet():

    def __init__(self):
        self.places = {}
        self.transistion = {}
        self.edgeTS = {}
        self.edgeST = {}
    def add_place(self, name):
        self.places[name] = 0
        return self

    def add_transition(self, name, id):
        self.transistion[name] = id
        return self
    def transition_name_to_id(self, name):
        return self.transistion[name]
    def add_edge(self, source, target):
        self.edgeTS.setdefault(target, []).append(source)
        self.edgeST.setdefault(source, []).append(target)
        return self
    def get_tokens(self, place):
        return self.places[place]

    def is_enabled(self, transition):
        result = self.edgeTS.setdefault(transition,[])
        for i in result:
            if self.places[i] ==0:
                return False
        return True

    def add_marking(self, place):
        self.places[place] = self.places[place] + 1

    def fire_transition(self, transition):
        if self.is_enabled(transition):
            for i in self.edgeTS[transition]:
                self.places[i] = self.places[i] - 1
            for i in self.edgeST[transition]:
                self.places[i] = self.places[i] + 1
            return True
        return False

#
p = PetriNet()

p.add_place(3)  # add place with id 1
p.add_place(4)
p.add_place(6)
p.add_place(7)
p.add_transition("A", -1)  # add transition "A" with id -1
p.add_transition("B", -2)
p.add_transition("C", -3)
p.add_transition("D", -4)

p.add_edge(3, -1)
p.add_edge(-1, 4)
p.add_edge(4, -2).add_edge(-2, 6)
p.add_edge(4, -3).add_edge(-3, 6)
p.add_edge(6, -4)
p.add_edge(-4, 7)

print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.add_marking(3)  # add one token to place id 1
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-1)  # fire transition A
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-3)  # fire transition C
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-4)  # fire transition D
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.add_marking(4)  # add one token to place id 2
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-2)  # fire transition B
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-4)  # fire transition D
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

# by the end of the execution there should be 2 tokens on the final place
print(p.get_tokens(7))