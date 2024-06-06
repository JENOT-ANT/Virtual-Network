
class Packet:
    source: tuple[str, int]
    destination: tuple[str, int]
    data: str

    def __init__(self, source: tuple[str, int], destination: tuple[str, int], data: str):
        self.source = source
        self.destination = destination
        self.data = data


class File:
    owner: str # always has all permissions to the file

    # only permissions for "others" cathegory (as groups aren't implemented and owner has all by default)
    r: bool # read / list files
    w: bool # write / add, remove files
    x: bool # execute / enter

    def __init__(self, owner: str, r: bool, w: bool, x: bool):
        self.owner = owner
        self.r = r
        self.w = w
        self.x = x


class TextFile(File):
    content: str

    def __init__(self, content: str, owner: str = "root", r: bool = True, w: bool = False, x: bool = True):
        super().__init__(owner, r, w, x)
        self.content = content
        

class Directory(File):
    files: dict[str, File] # file_name: TextFile | Directory

    def __init__(self, files: dict[str, File] | None = None, owner: str = "root", r: bool = True, w: bool = False, x: bool = True):
        super().__init__(owner, r, w, x)
        self.files = files if files is not None else {}


class Process:
    user: str
    path: str


class VM:
    ip: str
    hard_disk: Directory
    
    cpu: list[Process]
    
    # RAM:
    net_in: list[Packet]
    net_out: list[Packet]
    udp_interface: dict[int, Packet] # port: Packet

    ostream: str | None

    def __init__(self, ip: str):
        self.ip = ip
        self.hard_disk = Directory()
        
        self.cpu = []
        
        self.net_in = []
        self.net_out = []
        self.udp_interface

        self.ostream = None


    def read_ostream(self) -> str:
        """Returns and resets ostream. If ostream is empty <=> None, ValueError is rised."""
        if self.ostream is None:
            raise ValueError
        
        output: str  = self.ostream
        self.ostream = None
        return output


    def boot(self):
        self.hard_disk.files["etc"] = Directory(r = True, w = False, x = False)
        
        self.hard_disk.files["bin"] = Directory()
        self.hard_disk.files["home"] = Directory()
        self.hard_disk.files["tmp"] = Directory()
    

