from VM import VM


MAX_MEMBERS: int = 12

RANKS: dict = {
    'Apprentice': 0,
    'Sergeant': 1,
    'Co-Captain': 2,
    'Captain': 3,
}

INT_TO_RANK: tuple = ('Apprentice', 'Sergeant', 'Co-Captain', 'Captain',)


class Squad:
    name: str
    members: dict[str, int]# {nick: role}
    recruting: bool

    def __init__(self, name: str, members: dict, recruting: bool):
        self.name = name
        self.members = {}
        self.recruting = recruting

        for member in members:
            self.members[member] = members[member]

    def add_member(self, nick: str) -> bool:
        if len(self.members) >= MAX_MEMBERS or self.recruting is False:
            return False
        
        self.members[nick] = RANKS['Apprentice']
        return True

    def promote(self, operator: str, nick: str) -> bool:
        if not nick in self.members or self.members[nick] + 1 > RANKS['Captain'] or self.members[operator] <= self.members[nick]:
            return False
        
        self.members[nick] += 1 
        return True
        
    def demote(self, operator: str, nick: str) -> bool:
        if not nick in self.members or self.members[operator] <= self.members[nick]:
            return False
        
        if self.members[nick] > RANKS['Apprentice']:
            self.members[nick] -= 1
        else:
            self.members.pop(nick)

        return True

    def panel(self) -> str:
        output: str

        output = f"""
________________________________
|{               self.name:^30}|
|==============================|
|{f' members: {len(self.members)}/{MAX_MEMBERS}':<30}|
|{f' recruitment: {self.recruting}':<30}|
|==============================|"""

        for member in self.members.keys():
            output += f"\n|{member:^14}|{INT_TO_RANK[self.members[member]]:^15}|"

        output += "\n|______________________________|"

        return output


    def export(self) -> dict:
        return {
            'name': self.name,
            'members': self.members,
            'recruting': self.recruting,
        }
    