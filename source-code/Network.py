from VM import VM, NetInterface
from random import randint
import shelve

DATABASE: str = 'vhn-database'
SYSTEM_IP: str = '0.0.0.0'

class Network:
    by_ip: dict[str, VM] # IP: VM
    dns: dict[str, str] # nick: IP
    
    system_net: NetInterface

    def save(self):
        shelf: shelve.Shelf = shelve.open(DATABASE)
        
        shelf['vms'] = self.by_ip

        shelf.close()

    def load(self):
        shelf: shelve.Shelf = shelve.open(DATABASE)
        
        if 'vms' in shelf.keys():
            self.by_ip = shelf['vms']

        shelf.close()
    
    def change_nick(self, old_nick: str, new_nick: str) -> bool:
        vm: VM
        
        if new_nick in self.dns.keys():
            return False
        
        vm = self.by_ip[self.dns[old_nick]]
        
        vm.nick = new_nick
        self.dns[new_nick] = self.dns.pop(old_nick)

        return True

    def create_vm(self, user_id: int, nick: str) -> bool:
        ip: str
        
        if nick in self.dns.keys():
            return False

        ip = self.__generate_ip__()
        
        self.by_ip[ip] = VM(user_id, ip, nick)
        self.dns[nick] = ip

        return True
    
    def forward_net(self) -> None:
        target: VM

        for vm in self.by_ip.values():
            for packet in vm.network.traffic_out:
                if not packet.destination[0] in self.by_ip.keys():
                    self.system_net.send(0, packet.source, 'Address not found!')
                    continue
                
                target = self.by_ip[packet.destination[0]]
                target.network.traffic_in[packet.destination[1]] = packet
            
            vm.network.traffic_out.clear()

    def cpu(self):
        while True:
            self.forward_net()

    def __init__(self):
        self.system_net = NetInterface(SYSTEM_IP)
        
        self.by_ip = {}
        self.dns = {}
        
        self.load()
        self.__prepare_dns__()

        print(self.dns)

    
    def __prepare_dns__(self):
        for ip in self.by_ip.keys():
            self.dns[self.by_ip[ip].nick] = ip

    def __generate_ip__(self) -> str:
        ip: str = f'{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}'
        
        while ip in self.by_ip.keys() or ip == self.system_net.ip:
            ip = f'{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}'
        
        return ip
    