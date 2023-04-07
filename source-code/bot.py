import discord
from Network import Network
from VM import BOT_USER_ID

ACTIVITY: str = 'Hacking the Planet!'
ROLES: dict[str, discord.Color] = {
    'Hacker': discord.Color.blue(),
    'Co-Leader': discord.Color.yellow(),
    'Leader': discord.Color.gold(),
    'Recruit': discord.Color.blurple(),
}

class Bot:
    client: discord.Client
    tree: discord.app_commands.CommandTree[discord.Client]
    network: Network

    def fix_nicks(self) -> None:
        user: discord.User | None

        for vm in self.network.by_ip.values():
            
            if vm.user_id == BOT_USER_ID:
                continue

            user = self.client.get_user(vm.user_id)
            
            if user != None and user.display_name != vm.nick:
                if self.network.change_nick(vm.nick, user.display_name) is False:
                    print('# Nicknames confilct!')


    def __init__(self) -> None:
        self.client = discord.Client(intents=discord.Intents.all(), activity=discord.Game(ACTIVITY))
        self.tree = discord.app_commands.CommandTree(self.client)
        self.network = Network()

        @self.client.event
        async def on_ready() -> None:
            roles: list[str]

            self.fix_nicks()
            await self.tree.sync()

            for guild in self.client.guilds:
                roles = [role.name for role in guild.roles]
                
                for role in ROLES.keys():
                    if not role in roles:
                        await guild.create_role(name=role, permissions=discord.Permissions.none(), color=ROLES[role])

        @self.client.event
        async def on_member_update(before: discord.Member, after: discord.Member) -> None:
            if before.nick != after.nick:
                self.network.change_nick()

        @self.tree.command(name='save')
        async def save(cmd: discord.Interaction) -> None:
            '''Save game progress'''
            self.network.save()
            await cmd.response.send_message('Progress saved.', ephemeral=True)

        @self.tree.command(name='register')
        async def register(cmd: discord.Interaction, new_nick: str|None=None) -> None:
            '''Initialize your player profile'''
            
            if new_nick == None:
                new_nick = cmd.user.display_name
            
            if new_nick in self.network.dns.keys():
                await cmd.response.send_message('Your nick/name is already in use :(', ephemeral=True)
                return
            
            self.network.create_vm(cmd.user.id, new_nick)

            await cmd.response.send_message('You are in!', ephemeral=True)
        

    def run(self, api_token: str) -> None:
        self.client.run(api_token)
