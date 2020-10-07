"""
Khem Holden 1/2/2019
base program for implementing scum aka president in discord
scum is a 4 player card game where the objective is to get rid of all your cards
rules:
turn order the turns go from player to player until they cant play and pass their turn
this implementation reqiures you to pass manually and doesnt check if you do it automatically

you can only play if the cards you are going to play match whats happening on the board
example: if the starting player played a single card, then everyone else can only play single cards
same goes for doubles, triples, straights, and suited straights********to be implemented at a later date

there are power hands called bombs, poisons, and spikes
bombs: straight of doubles example: 33,44,55
poisons: four of a kind
spikes: consecutive triples :333,444
bombs beat standard play poisons beat bombs and spikes beat everything

you can only play your hand if it beats the last hand or ties it

first one to get rid of their cards gets rank of president
second gets vice president
third gets secretary
fourth gets scum
at the beginning of the next round the president can swap 2 of any card from scum
vp can swap 1 card with secratary

This specific file handles the discord user itneraction and main game flow
"""
#TODO LIST
#proper error handling eg:send the problem with the users play in the channel, for example straight isnt consecutive
#make it so that if there are more than 4 people who want to play then the scum gets switched out for them
#make it so that players can rearrange cards in their hand



import discord
import scumClasses
from scumClasses import CardSuit,CardValue
import threading
import io
from PIL import Image

deck = scumClasses.Deck();

valid = 1 #while the users still want to play
loop = 0  #used for making sure that there is no trading on the first loop

#function for the main logic for trading cards at the beginning of a new loop

async def presTrade(pres,scum,channel):
	take = False #for if the cads taken arent in the scums hand
	while(take == False):	#while taking the cards isnt successful
		await channel.send(f'```{pres.user.display_name} choose the 2 cards you want from the scum```')
		takeString = await client.wait_for('message', check=lambda m: m.channel == channel and pres.user == m.author)
		take = pres.takeCards(scum,takeString,channel)
	give = False #this part is the same as take but instead you give 2 cards
	while (give == False):
		await channel.send(f'```{pres.user.display_name} choose the 2 cards you want to give to the scum```')
		
		give = pres.giveCards(scum,takeString,channel)
#could technically just have these 2 as 1 function only difference is the print statements
async def vpTrade(vp,sec,channel):
	take = False
	while(take == False):
		channel.send(f'```{vp.user.display_name} choose the card you want from the secretary```')
		takeString = await client.wait_for('message', check=lambda m: m.channel == channel and vp.user == m.author)
		take = vp.takeCards(sec,takeString,channel)
	give = False
	while (give == False):
		channel.send(f'```{vp.user.display_name} choose the card you want to give to the scum```')
		give = vp.giveCards(sec,takeString,channel)

#function for sending an image to player/channel
async def imageSend(cards,reciever):
	#get the width of a card(useul if the sie ever changes)
	image = Image.open('CardImages\\' + repr(cards[0])+ '.png')
	width,height = image.size
	image.close()
	#create a blank image with no background
	toSend = Image.new('RGBA',(width*len(cards),height))
	i = 0
	for card in cards:
		#open the image that corresponds to the card and paste it in the image to send to the player/channel
		image = Image.open('CardImages\\' + repr(card)+ '.png')
		toSend.paste(image,(i,0))
		image.close()
		i = i+width
	#save the image because sending from memory doesn't work 
	toSend.save('temphand.png','PNG')
	toSend.close()
	#send the image
	handmsg = await reciever.send(file = discord.File('temphand.png'))
	return handmsg
#function that contains the game
async def mainScum(initialPlayerList,channel,client):
	
	deck.initDeck()#initialize the deck 
	playerList = []#initialize the list of players
	valid = 1
	#main loop and game logic for the game
	while(valid == 1):
		#the first time the game is ran, create the players and deal the deck
		message = []
		if loop == 0:
			#initialize the players to the player class
			player1 = scumClasses.Player(initialPlayerList[0])
			player2 = scumClasses.Player(initialPlayerList[1])
			player3 = scumClasses.Player(initialPlayerList[2])
			player4 = scumClasses.Player(initialPlayerList[3])
			playerList = [player1,player2,player3,player4]
			deck.dealDeck(playerList)
			#sort each users hand and send it to the user
			
			for player in playerList:
				await player.user.send('deleting')
				userdm = player.user.dm_channel
				async for todelete in userdm.history(limit=1000):
					await todelete.delete()
				player.sortCards()	#sort the deck to make it easier for the players,
				playermsg = await player.user.send('your hand is:')
				handmsg = await imageSend(player.hand,player.user)
				message.append(playermsg)
				message.append(handmsg)
		#if its not the first time then there should be trading between players
		else:
			deck.initDeck()
			deck.dealDeck(playerList)
			for player in playerList:
				await player.user.send('deleting')
				userdm = player.user.dm_channel
				async for todelete in userdm.history(limit=1000):
					await todelete.delete()
				player.sortCards()
				playermsg = await player.user.send('your hand is:')
				handmsg = await imageSend(player.hand,player.user)
				message.append(playermsg)
				message.append(handmsg)
			#sort out the ranks for trading
			for x in playerList:
				if x.rank == 1:
					president = x
				elif x.rank == 2:
					vp = x
				elif x.rank == 3:
					sec = x
				elif x.rank == 4:
					scum = x
			#use multithreading so that the trading happens at the same time
			#this is just for saving time trading in case people are impatient
			t1 = threading.Thread(target = presTrade,args=(pres,scum,channel))
			t2 = threading.Thread(target = vpTrade,args=(vp,sec,channel))
			t1.start()
			t2.start()
			t1.join()
			t2.join()
			j = 0
			for player in playerList:
				player.sortCards()
				playermsg = await player.user.send('your hand is now:')
				handmsg = await imageSend(player.hand,player.user)
				message[j].delete()
				message[j+1].delete()
				message[j] = playermsg
				message[j+1] = handmsg
				j = j+2
		#the person who starts is the person with the three of clubs
		for x in playerList:
			if (scumClasses.Card(CardValue.Three,CardSuit.Clubs)) in x.hand:
				x.isTurn = True	
				playernum = playerList.index(x)
			else:
				#make sure that its no one elses turn
				x.isTurn = False
		playersLeft = 4#set the numbers of players with cards
		firstTurn = True #everyone has full hands, needed to check if the first play is the 3 of clubs
		playersIn = 4
		firstRound = 0
		while playersLeft > 1:	#players with card left
		
			lastPlay = scumClasses.Play([])#the last hand played for checking if the played hand beats it
			#loop for setting status and players still left
			playersIn = 0
			for player in playerList:
				if player.playStatus != 2:
					player.playStatus = 0#reset the players status for the next round
					playersIn += 1#players that havent skipped or finished
			await channel.send("```new round```")
			playerDoneflag = 0
			while playersIn >0:	#while players are still in the round
				playerFlag = 0
				for player in playerList:
					if (playerDoneflag == 1):
						for tempplayer in playerList:
							if tempplayer.playStatus == 0:
								playerFlag = 1

					if playerFlag == 1 or (playerDoneflag == 0 and playersIn >1):
						#need playersin>1 because it can go from player 0 passing and only player 3 left
						if player.isTurn and player.playStatus == 0 and playersIn > 0:
							
							index = playerList.index(player)
							print(index)
							print(playersIn)
							await channel.send(player.user.mention +"'s turn")#make sure the user knows its their turn maybe better to have @user to make a discord notification
							validplay = False#for the loop checking if their play was valid
							
							#copy the pards into another list
							#the reason for this is because if the play isnt valid, we dont want lastPlaay to be overwritten since just having = makes nextLastPlay a pointer to lastPlay
							nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
							nextLastPlay.special = lastPlay.special
							#while the user hasn't sent a valid play
							while validplay == False:
								#inform the user how to send their play
								for tempPlayer in playerList:
									await channel.send(f'{player.user.name} has {len(player.hand)} cards left')
								
								await channel.send('```type the cards you wish to play in the form of value suit, value suit and so on```')
								#wait for the users play and check if it is actually that user in the right channel
								userplay = await client.wait_for('message', check=lambda m: m.channel == channel and player.user == m.author)
								#if the user skipped their turn, you can't skip on the very first turn
								if userplay.content == 'skip' or userplay.content == 'pass' and firstTurn == False:
									#make it so that the user is not in the round anymore and the players in is 1 less
									player.playStatus = 1
									playersIn -= 1
									validplay = True
								else:
									#call the function for playing the cards, this function converts the users string as well as checks if its valud
									try:
										nextLastPlay,validplay = await player.playCards(userplay.content, firstTurn, nextLastPlay,channel)
									except AttributeError:
										validplay = False
									#if its not valid reset the last play, I think the resetting can go at the beginning of the while loop so that it saves 3 lines
									if validplay == False:
										await channel.send("```Please try again with a proper input```")
										nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
										nextLastPlay.special = lastPlay.special
									else:
										#if the play was valid send it in the main channel for people to see
										await channel.send(f'```played:```')
										await imageSend(nextLastPlay.cards,channel)
										
							#now that its not the first turn set this to false, this will be set every loop, could put an if statement but it wouldnt improve runtime
							firstTurn = False
							#set the last play to be the temporary since it is valid
							lastPlay.cards = nextLastPlay.cards.copy()
							lastPlay.special = nextLastPlay.special
							
							
							#if the player has 0 cards left
							if player.playStatus == 2:
								playerDoneflag = 1
								#set their rank and then subtract based off of the number of players left, could also subtract and then do 4-players left
								player.rank = 5-playersLeft
								#tell the player the position they finished
								await channel.send(f'```{player.user.display_name} finished in position {player.rank}```')
								playersLeft -= 1
								playersIn -= 1
								#if theres only 1 player left theyre automatically scum
								print(f'players left = {playersLeft}')
								if playersLeft == 1:
									if playerList[(index+1)%4].playStatus == 0 or playerList[(index+1)%4].playStatus == 1:
										playerList[(index+1)%4].rank = 4
										playerList[(index+1)%4].playStatus = 2
										await channel.send(f'```{playerList[(index+1)%4].user.display_name} finished in position {playerList[(index+1)%4].rank}```')
										await message[((index+1)%4)*2].delete()
										await message[((index+1)%4)*2 +1].delete()
									elif playerList[(index+2)%4].playStatus == 0 or playerList[(index+2)%4].playStatus == 1:
										playerList[(index+2)%4].rank = 4
										playerList[(index+2)%4].playStatus = 2
										await channel.send(f'```{playerList[(index+2)%4].user.display_name} finished in position {playerList[(index+2)%4].rank}```')
										await message[((index+2)%4)*2].delete()
										await message[((index+2)%4)*2 +1].delete()
									elif playerList[(index+3)%4].playStatus == 0 or playerList[(index+3)%4].playStatus == 1:
										playerList[(index+3)%4].rank = 4
										playerList[(index+3)%4].playStatus = 2
										await channel.send(f'```{playerList[(index+3)%4].user.display_name} finished in position {playerList[(index+3)%4].rank}```')
										await message[((index+3)%4)*2].delete()
										await message[((index+3)%4)*2 +1].delete()
							#send the player their updating hand if they havent passed
							if player.playStatus != 1:
								await message[index*2].delete()
								await message[index*2 +1].delete()
								#if the player is done then dont send any cards
								if len(player.hand) != 13 and len(player.hand) != 0:
									playermsg = await player.user.send('your hand is now:')
									handmsg = await imageSend(player.hand,player.user)
									message[index*2] = playermsg
									message[index*2 +1] = handmsg
								
							#if there is still a person in, set their turn as the next one
							#doesnt matter if the round finished since turns will be overwritten
							player.isTurn = False
							
							if playerList[(index+1)%4].playStatus == 0:
								playerList[(index+1)%4].isTurn = True
							elif playerList[(index+2)%4].playStatus == 0:
								playerList[(index+2)%4].isTurn = True
							elif playerList[(index+3)%4].playStatus == 0:
								playerList[(index+3)%4].isTurn = True
							elif playerList[(index+1)%4].playStatus == 1 and player.playStatus ==1:
								playerList[(index+1)%4].isTurn = True
							elif playerList[(index+2)%4].playStatus == 1 and player.playStatus ==1:
								playerList[(index+2)%4].isTurn = True
							elif playerList[(index+3)%4].playStatus == 1 and player.playStatus ==1:
								playerList[(index+3)%4].isTurn = True
					else:
						playersIn = playersIn-1
					#almost exact copy of the previous if statement, the only difference is setting the turns
					#if I wanted to make it shorter I would use the playerlsit and a for loop so that it would be
					#if player.isTurn and player.playStatus == 0
					#then settting turns would be for i in len(playerList) if player[current user + i %4] set the turn same for rank
					#and you would keep track of the players index using index = index + 1 %4
				
				
		#check if the users want to play another round
		await channel.send("```play another round?```")
		#it shouldnt matter who says no
		response = await client.wait_for('message')
		if (response == 'no'):
			valid = 0