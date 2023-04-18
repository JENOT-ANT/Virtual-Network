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
        
        await cmd.response.send_message(f'{cmd.user.mention}\n```js\n{self.network.ssh(self.network.by_id[cmd.user.id])}\n```')

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
        
        @self.tree.command(name='mod')
        async def mod(cmd: discord.Interaction, new_mod: discord.Member):
            '''Set the moderator status for the member.'''
            
            if not cmd.user.id in self.network.mods:
                await cmd.response.send_message('Errmmm... Maybe no?')
                return
            
            self.network.mods.append(new_mod.id)
            await cmd.response.send_message(f'{new_mod.mention}\nWelcome to the moderation team!')
        
        @self.tree.command(name='close')
        async def close(cmd: discord.Interaction, save: bool=True):
            '''Shut down the bot'''
            if not cmd.user.id in self.network.mods:
                await cmd.response.send_message('You are not permited to shut down the whole game... If you think there is an error and something is not working properly, contact game moderator.', ephemeral=True)
                return
            
            if save is True:
                self.network.save()
            
            self.network.running = False
            self.cpu_loop.join()
            
            await cmd.response.send_message('Shutting down...')
            await self.client.close()
            

        @self.tree.command(name='save')
        async def save(cmd: discord.Interaction) -> None:
            '''Save game progress'''
            self.network.save()
            await cmd.response.send_message('Progress saved.', ephemeral=True)

        @self.tree.command(name='register')
        async def register(cmd: discord.Interaction, new_nick: str|None=None, os: str|None=None) -> None:
            '''Initialize your player profile'''
            
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

            if os == None:
                os = OS_LIST[randint(0, len(OS_LIST) - 1)]

            self.network.add_vm(new_nick, OS_LIST.index(os), None, cmd.user.id)
            
            if cmd.guild != None:
                for role in cmd.guild.roles:
                    if role.name == 'Hacker':
                        await cmd.user.add_roles(role)
            
            await cmd.response.send_message(f'{cmd.user.mention}\nWelcome to the Exclusive-Virtual-Network-Playground!')
        
        @self.tree.command(name='list-squads')
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
            
            await cmd.response.send_message(f'{cmd.user.mention}\n```\n{squad_list}\n```')
        
        @self.tree.command(name='join-squad')
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
            
            await cmd.response.send_message(f'{cmd.user.mention} Welcome to {squad_name}!')

        @self.tree.command(name='rename')
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
            await cmd.response.send_message(f'{cmd.user.mention} Your new in-game nick is: {new_nick}', ephemeral=True)

        @self.tree.command(name='-panel-')
        async def panel(cmd: discord.Interaction):
            '''Display dashboard with info about the VM of currently logged-in user'''
            await self.__ssh__('panel', cmd)
        
        @self.tree.command(name='-ls-')
        async def ls(cmd: discord.Interaction):
            '''List files of currently logged-in user'''
            await self.__ssh__('ls', cmd)
        
        @self.tree.command(name='-cat-')
        async def cat(cmd: discord.Interaction, file_name: str) -> None:
            '''
            Display content of the file
            
            Parameters
            ----------
            file_name : str
                Name of the file to display
            '''
            await self.__ssh__(f'cat {file_name}', cmd)

        @self.tree.command(name='-ps-')
        async def ps(cmd: discord.Interaction):
            '''Display currently running processes'''
            
            await self.__ssh__('ps', cmd)
        
        @self.tree.command(name='-whoami-')
        async def whoami(cmd: discord.Interaction):
            '''Display currently-logged user's nick and IP'''
            await self.__ssh__('whoami', cmd)

        @self.tree.command(name='archives')
        async def archives(cmd: discord.Interaction):
            ...

    def run(self, api_token: str) -> None:
        self.client.run(api_token)
