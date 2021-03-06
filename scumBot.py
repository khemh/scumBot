import discord
import discordscum
from discord.ext.commands import Bot


BOT_PREFIX = ("s!", "s! ")
TOKEN = 

client = Bot(command_prefix=BOT_PREFIX)

#list of channel ids
# make passing non case sensitive
# proper error handling
# allow people to rearrange cards
# set the persons turn properly if theres 2 people in out of 4 and 1 person finishes

@client.event
async def on_ready():
	#prints out the bot used to see if its running
	print(f'Logged in as {client.user}')

@client.command(name='at',help = '@s the user')
async def at(message):
	channel = message.channel
	await channel.send(message.author.mention +"'s turn")
#running the scum program
@client.command(name='scum',help ='Starts a game of scum type s!rules for the rules of the game')
async def scum(message):
	channel = message.channel
	await channel.send("```Starting scum game, waiting for 4 players to join```")
	await channel.send("```Join by typing join```")
	#wait for 4 players to join
	playerList = []
	
	def joincheck(m):
		return m.content == 'join' and m.channel == channel
		
	while(len(playerList)< 4):
		#players can join twice
		usrmsg = await client.wait_for('message', check=joincheck)
		#if usrmsg.author not in playerList:
		playerList.append(usrmsg.author)
	#TODO add a space between each player
	await channel.send(f'```Players joined: {playerList[0].display_name} {playerList[1].display_name} {playerList[2].display_name} {playerList[3].display_name}```')
	#now move on to main scum file
	#delete the dms first just in case theres leftover cards
	for player in playerList:
		await player.send('deleting')
		userdm = player.dm_channel
		async for todelete in userdm.history(limit=1000):
			await todelete.delete()
	await discordscum.mainScum(playerList,channel,client)
	
@client.command(name='cleardm',help ='clears the bots sent messages in dm')
async def cleardm(message):
	await message.author.send('deleting')
	userdm = message.author.dm_channel
	async for message in userdm.history(limit=1000):
		await message.delete()

@client.command(name='rules',help ='displays the rules for the game')
async def rules(message):
	channel = message.channel
	await channel.send("""```turn order: the turns go from player to player until they cant play and pass their turn
this implementation reqiures you to pass manually and doesnt check if you can't make a play

you can only play if the cards you are going to play match whats happening on the board
example: if the starting player played a single card, then everyone else can only play single cards
same goes for doubles, triples, straights, and suited straights********to be implemented at a later date

there are special hands called bombs, poisons, and spikes that beat regular plays
bombs: straight of doubles example: 33,44,55
poisons: four of a kind
spikes: consecutive triples :333,444
bombs are the lowest tier of special hands, poisons beat bombs, and spikes beat everything

you can only play your hand if it beats the last hand or ties it

first player to get rid of their cards gets rank of president
second gets vice president
third gets secretary
fourth gets scum
at the beginning of the next round the president can swap 2 cards with scum
vp can swap 1 card with secratary

Play a hand using the form value,value,etc or value suit,value suit for example 3,3 or 3 c, 3 s or 3 of clubs, 3 of spades```""")

client.run(TOKEN)
#client.close()