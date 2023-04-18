from VM import VM


MAX_MEMBERS: int = 12

RANKS: dict = {
    "Apprentice": 0,
    "Sergeant": 1,
    "Co-Captain": 2,
    "Captain": 3,
}

INT_TO_RANK: tuple = ("Apprentice", "Sergeant", "Co-Captain", "Captain",)


class Squad:
    name: str
    members: dict[str, int]# {nick: role}
    recruting: bool

    def __init__(self, name: str, members: dict, recruting: bool):
        self.name = name
        self.members = members
        self.recruting = recruting

    def add_member(self, nick: str, rank: str='Apprentice'):
        self.members[nick] = RANKS[rank]

    def promote(self, nick: str):
        ...
        
    def demote(self, nick: str):
        ...

    def panel(self) -> str:
        output: str

        output = f"""
 ______________________________
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
            "name": self.name,
            "members": self.members,
            "recruting": self.recruting,
        }
    