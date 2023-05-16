from functools import wraps
import discord
from Network import Network
from threading import Thread
from Squad import RANKS, MAX_MEMBERS
from VM import OS_LIST
from random import randint

ADMIN: int = 997119789329825852
ACTIVITY: str = 'Hacking the Planet!'
MAX_NAME_LENGTH: int = 12


ROLES: dict[str, discord.Color] = {
    'Captain': discord.Color.gold(),
    'Co-Captain': discord.Color.yellow(),
    'Sergeant': discord.Color.teal(),
    'Apprentice': discord.Color.blurple(),
    'Hacker': discord.Color.blue(),
}

INSTRUCTION: str = '''

# STARTUP:
  1. Use `/register` command to init your game virtual machine (called VM).
  2. You can communicate with your VM using commands formated like this: `-cmd-`.
  3. Use `/-panel-` command to view basic info about your VM.
  4. Use `/help topic` command to display more bright explanations about the topic.

----------------------------------------

# LIST OF TOPICS:
  `software` -> basic info about software running on VMs
  `hack` -> guid how to hack (in-game)

'''

SOFTWARE_HELP: str = '''
SOFTWARE:

'''
HACK_HELP: str = '''
HOW TO HACK:

'''

class Bot:
    client: discord.Client
    tree: discord.app_commands.CommandTree[discord.Client]
    network: Network
    cpu_loop: Thread

    async def __ssh__(self, cmd_text: str, cmd: discord.Interaction):
        ip: str
        port: int
        nick: str

        if not cmd.user.id in self.network.by_id.keys():
            await cmd.response.send_message('You are not registered... Check `/register`', ephemeral=True)
            return
        
        ip = self.network.by_id[cmd.user.id].ip
        port = self.network.by_id[cmd.user.id].port_config["ssh"]
        nick = self.network.by_id[cmd.user.id].nick

        self.network.direct_send((ip, port), (nick, None), cmd_text)
        
        await cmd.response.send_message(f'```js\n{self.network.ssh(self.network.by_id[cmd.user.id])}\n```', ephemeral=True)
    
    def __log__(self, cmd_function):
        @wraps(cmd_function)
        async def log(*args, **kwargs):
            print(f'{args[0].guild.name if args[0].guild != None else "dm"} -> {args[0].user.name}: {args[0].command.name if args[0].command != None else "Not Recognised"}')
            
            return await cmd_function(*args, **kwargs)
        
        return log

    def __wrapped__(self, text: str, color: bool=False):
        return f'```{"js" if color is True else ""}\n{text}\n```'

    def __init__(self) -> None:
        self.client = discord.Client(intents=discord.Intents.all(), activity=discord.Game(ACTIVITY))
        self.tree = discord.app_commands.CommandTree(self.client)
        self.network = Network('vhn-database', ADMIN)
        self.cpu_loop = Thread(target=self.network.cpu_loop)

        self.cpu_loop.start()

        @self.client.event
        async def on_ready() -> None:
            roles: list[str]

            await self.tree.sync()

            for guild in self.client.guilds:
                roles = [role.name for role in guild.roles]
                
                for role in ROLES.keys():
                    if not role in roles:
                        await guild.create_role(name=role, permissions=discord.Permissions.none(), color=ROLES[role])
        
        # @self.tree.command(name='mod')
        # async def mod(cmd: discord.Interaction, new_mod: discord.Member):
        #     '''Set the moderator status for the member.'''
            
        #     if not cmd.user.id in self.network.mods:
        #         await cmd.response.send_message('Errmmm... Maybe no?')
        #         return
            
        #     self.network.mods.append(new_mod.id)
        #     await cmd.response.send_message(f'{new_mod.mention}\nWelcome to the moderation team!')

        @self.tree.command(name='close')
        @self.__log__
        async def close(cmd: discord.Interaction, save: bool=True):
            '''Shut down the bot'''

            if not cmd.user.id in self.network.mods:
                await cmd.response.send_message('You are not permited to shut down the whole game... If you think there is an error and something is not working properly, contact game moderator.', ephemeral=True)
                return
            
            if save is True:
                self.network.save()
            
            self.network.running = False
            self.cpu_loop.join()
            
            await cmd.response.send_message('Shutting down...', ephemeral=True)
            await self.client.close()
        
        @self.tree.command(name='help')
        @self.__log__
        async def help(cmd: discord.Interaction, topic: str|None=None):
            '''Display game instructions'''

            if topic == None:
                await cmd.response.send_message(INSTRUCTION, ephemeral=True)
            elif topic.lower() == 'software':
                await cmd.response.send_message(SOFTWARE_HELP, ephemeral=True)
            elif topic.lower() == 'hack':
                await cmd.response.send_message(HACK_HELP, ephemeral=True)
            else:
                await cmd.response.send_message('Topic not found. Try `/help` without any topic to display the topic list.', ephemeral=True)

        @self.tree.command(name='save')
        @self.__log__
        async def save(cmd: discord.Interaction) -> None:
            '''Save game progress.'''

            self.network.save()
            await cmd.response.send_message('Progress saved.', ephemeral=True)

        @self.tree.command(name='register')
        @self.__log__
        async def register(cmd: discord.Interaction, new_nick: str|None=None, vm_os: str|None=None) -> None:
            '''
            Initialize your player profile. OS list: Penguin, Parrot, Racoon, Turtle
            
            Parameters
            ----------
            new_nick : str
                Your new in-game nick
            vm_os : str
                A virtual OS of your new virtual machine (Penguin, Parrot, Racoon, Turtle)
            '''

            if cmd.user.id in self.network.by_id.keys():
                await cmd.response.send_message('I\'m almost sure, you have an account already... If you lost access to it -> just contact game moderator for help.', ephemeral=True)
                return
            
            # if not squad in self.network.squads.keys():
            #     await cmd.response.send_message('Ther is no squad with such a name, try: `/list-squads` cmd.', ephemeral=True)
            #     return
            
            # if self.network.squads[squad].recruting is False:
            #     await cmd.response.send_message(f'The squad {squad} is not recruiting for now...')

            if new_nick == None:
                new_nick = cmd.user.display_name

            if new_nick in self.network.by_nick.keys():
                await cmd.response.send_message('It seems that this nick is registered already... Maybe try something different.', ephemeral=True)
                return

            if vm_os == None:
                vm_os = OS_LIST[randint(0, len(OS_LIST) - 1)]

            self.network.add_vm(new_nick, OS_LIST.index(vm_os), None, cmd.user.id)
            
            if cmd.guild != None:
                for role in cmd.guild.roles:
                    if role.name == 'Hacker':
                        await cmd.user.add_roles(role)
            
            await cmd.response.send_message(f'{cmd.user.mention}\nWelcome to the Exclusive-Virtual-Network-Playground!')
        
        @self.tree.command(name='list-squads')
        @self.__log__
        async def list_squads(cmd: discord.Interaction):
            '''Display a list of squads'''

            squad_list: str
            leader: str | None
            
            squad_list = f"   squad name    |members| state | captain\n{'=' * 42}\n"

            for squad in self.network.squads.values():
                leader = None
                for member in squad.members.keys():
                    if squad.members[member] == RANKS["Captain"]:
                        leader = member
                        break

                squad_list += f"{squad.name:^12} | {len(squad.members.keys()):2}/{MAX_MEMBERS} | {'open' if squad.recruting is True else 'close':5} | {leader}\n"
            
            await cmd.response.send_message(self.__wrapped__(squad_list), ephemeral=True)

        @self.tree.command(name='join-squad')
        @self.__log__
        async def join_squad(cmd: discord.Interaction, squad_name: str):
            '''
            Join a squad that is recruiting
            
            Parameters
            ----------
            squad_name : str
                Name of the squad you want to join
            '''

            if not cmd.user.id in self.network.by_id.keys():
                await cmd.response.send_message('You are not registered... Check `/register`', ephemeral=True)
                return
            if not squad_name in self.network.squads.keys():
                await cmd.response.send_message('There is no squad with such a name.', ephemeral=True)
                return
            if self.network.by_id[cmd.user.id].squad != None:
                await cmd.response.send_message('Your current squad needs you!', ephemeral=True)
                return

            self.network.join_squad(cmd.user.id, squad_name)
            
            if cmd.guild != None:
                for role in cmd.guild.roles:
                    if role.name == 'Apprentice':
                        await cmd.user.add_roles(role)
            
            await cmd.response.send_message(f'{cmd.user.mention} Welcome to **{squad_name}**! Contact the squad captain to get access to a private-channel/thread of your squad.')

        @self.tree.command(name='squad-panel')
        @self.__log__
        async def squad_panel(cmd: discord.Interaction):
            '''Display basic info about your squad'''
            squad_name: str | None

            if not cmd.user.id in self.network.by_id.keys():
                await cmd.response.send_message('You are not registered... Check `/register`', ephemeral=True)
                return
            
            squad_name = self.network.by_id[cmd.user.id].squad
            
            if squad_name == None:
                await cmd.response.send_message('You are not in a squad, are you?', ephemeral=True)
                return
            
            await cmd.response.send_message(self.__wrapped__(self.network.squads[squad_name].panel()), ephemeral=True)

        @self.tree.command(name='rename')
        @self.__log__
        async def rename(cmd: discord.Interaction, new_nick: str):
            '''
            Change in-game nickname
            
            Parameters
            ----------
            new_nick : str
                Your new in-game nick to set up
            '''

            if not cmd.user.id in self.network.by_id.keys():
                await cmd.response.send_message('You are not registered... Check `/register`', ephemeral=True)
                return

            if new_nick in self.network.by_nick.keys():
                await cmd.response.send_message('Nick already in use.', ephemeral=True)
                return
            
            if len(new_nick) > MAX_NAME_LENGTH:
                await cmd.response.send_message('Incorrect nick size.', ephemeral=True)
                return

            self.network.change_nick(cmd.user.id, new_nick)
            await cmd.response.send_message(f'{cmd.user.mention} Your new in-game nick is: {new_nick}')

        @self.tree.command(name='-panel-')
        @self.__log__
        async def panel(cmd: discord.Interaction):
            '''Display dashboard with info about the VM of currently logged-in user'''

            await self.__ssh__('panel', cmd)
        
        @self.tree.command(name='-ls-')
        @self.__log__
        async def ls(cmd: discord.Interaction):
            '''List files of currently logged-in user'''

            await self.__ssh__('ls', cmd)
        
        @self.tree.command(name='-cat-')
        @self.__log__
        async def cat(cmd: discord.Interaction, file_name: str) -> None:
            '''
            Display content of the file
            
            Parameters
            ----------
            file_name : str
                Name of the file to display
            '''

            await self.__ssh__(f'cat {file_name}', cmd)

        @self.tree.command(name='-rm-')
        @self.__log__
        async def rm(cmd: discord.Interaction, file_name: str) -> None:
            '''
            Remove the file from currently logged-in user
            
            Parameters
            ----------
            file_name : str
                Name of the file to remove
            '''
            await self.__ssh__(f'rm {file_name}', cmd)

        @self.tree.command(name='-ps-')
        @self.__log__
        async def ps(cmd: discord.Interaction):
            '''Display currently running processes'''

            await self.__ssh__('ps', cmd)
        
        @self.tree.command(name='-whoami-')
        @self.__log__
        async def whoami(cmd: discord.Interaction):
            '''Display currently-logged user's nick and IP'''
            await self.__ssh__('whoami', cmd)

        @self.tree.command(name='-transfer-')
        @self.__log__
        async def transfer(cmd: discord.Interaction, nick: str, amount: int):
            '''
            Transfer CV from currntly logged-in accunt to the account under the game-nick
            
            Parameters
            ----------
            nick : str
                In-game nick of the destination account to do the transfer
            
            amount : int
                Amount of money to transfer
            '''

            await self.__ssh__(f'transfer {nick} {amount}', cmd)

        @self.tree.command(name='--archives--')
        @self.__log__
        async def archives(cmd: discord.Interaction):
            '''List owned exploits'''

            if not cmd.user.id in self.network.by_id.keys():
                await cmd.response.send_message('You are not registered... Check `/register`', ephemeral=True)
                return
            
            await cmd.response.send_message(self.__wrapped__(self.network.by_id[cmd.user.id].archives()), ephemeral=True)
        
        @self.tree.command(name='--brute-force--')
        @self.__log__
        async def bf(cmd: discord.Interaction, passwd_hash: str):
            '''
            Brutforce the hash to find the password corresponding to it
            
            Parameters
            ----------
            passwd_hash : str
                Hashed password (from shadow.sys file) to be cracked
            '''
            
            if not cmd.user.id in self.network.by_id.keys():
                await cmd.response.send_message('You are not registered... Check `/register`', ephemeral=True)
                return

            await cmd.response.send_message(self.__wrapped__(self.network.start_bf(cmd.user.id, passwd_hash)), ephemeral=True)

        @self.tree.command(name='-whois-')
        @self.__log__
        async def whois(cmd: discord.Interaction, ip_address: str):
            '''
            Display squad and nick of the player with that IP
            
            Parameters
            ----------
            ip_address : str
                IP address to resolve
            '''
            if not ip_address in self.network.by_ip.keys():
                await cmd.response.send_message("IP address not found.", ephemeral=True)
                return
            
            await cmd.response.send_message(self.__wrapped__(f'{ip_address}:\n\tnick: {self.network.by_ip[ip_address].nick}\n\tsquad: {self.network.by_ip[ip_address].squad}'), ephemeral=True)

        @self.tree.command(name='--ai--')
        @self.__log__
        async def ai(cmd: discord.Interaction, lvl: int):
            '''
            Generate random-power exploit of the level specified

            Parameters
            ----------
            lvl : int
                Level of the exploit to create
            '''
            await cmd.response.send_message(self.__wrapped__(self.network.start_ai(cmd.user.id, lvl)), ephemeral=True)

        @self.tree.command(name='-exploit-')
        @self.__log__
        async def exploit(cmd: discord.Interaction, ip: str, port: int, exploit_id: int):
            '''
            Run the exploit with specified ID, against the target by given IP
            
            Parameters
            ----------
            ip : str
                IP address of the target to exploit
            port : int
                Port number on the target VM to send the exploit
            exploit_id : int
                ID of the exploit to run (check your exploit-list using `--archives--` cmd)
            '''
            await self.__ssh__(f'exploit {ip} {port} {exploit_id}', cmd)

        @self.tree.command(name='-scan-')
        @self.__log__
        async def scan(cmd: discord.Interaction, target_ip: str):
            '''
            Scan given IP for open ports and other details
            
            Parameters
            ----------
            target_ip : str
                IP address of the target VM to scan
            '''
            await self.__ssh__(f'scan {target_ip}', cmd)

        @self.tree.command(name='-exit-')
        @self.__log__
        async def exit(cmd: discord.Interaction):
            '''
            Close the last ssh connection (check `/-proxy-` cmd)
            '''

            await self.__ssh__('exit', cmd)
        
        @self.tree.command(name='-proxy-')
        @self.__log__
        async def proxy(cmd: discord.Interaction):
            '''
            Display your SSH connection path (VMs that you are connected to)
            '''

            await self.__ssh__('proxy', cmd)

    def run(self, api_token: str) -> None:
        self.client.run(api_token)