BOT_USER_ID: int = -1


class Packet:
    source: tuple[str, int]
    destination: tuple[str, int]

    contents: str

    def __init__(self, source: tuple[str, int], destination: tuple[str, int], contents: str):
        self.source = source
        self.destination = destination
        self.contents = contents

class NetInterface:
    ip: str
    traffic_in: dict[int, Packet] # port: Packet
    traffic_out: list[Packet]
    
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.traffic_in = {}
        self.traffic_out = []
    
    def send(self, port: int, destination: tuple[str, int], contents: str) -> None:
        self.traffic_out.append(Packet((self.ip, port), destination, contents))

    def recv(self, port: int) -> Packet:
        return self.traffic_in[port]

class VM:
    user_id: int
    nick: str
    wallet: int
    network: NetInterface

    def __init__(self, user_id: int, ip: str, nick: str):
        self.user_id = user_id
        self.nick = nick
        self.network = NetInterface(ip)
