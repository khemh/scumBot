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
#send the problem with the users play in the channel, for example straight isnt consecutive
#make it so that if there are more than 4 people who want to play then the scum gets switched out for them
#make it so that players can rearrange cards in their hand
#use images instead of cards when sending to the channel
#make the main player actions into a for loop to reduce number of lines

#delete the initial hand after you send another one

import discord
import scumClasses
from scumClasses import CardSuit,CardValue
import threading

deck = scumClasses.Deck();

valid = 1 #while the users still want to play
loop = 0  #used for making sure that there is no trading on the first loop

#function for the main logic for trading cards at the beginning of a new loop
async def presTrade(pres,scum,channel):
	take = False #for if the cads taken arent in the scums hand
	while(take == False):	#while taking the cards isnt successful
		await channel.send("```choose the 2 cards you want from the scum```")
		takeString = await client.wait_for('message', check=lambda m: m.channel == channel and pres.user == m.author)
		take = pres.takeCards(scum,takeString,channel)
	give = False #this part is the same as take but instead you give 2 cards
	while give == False :
		await channel.send("```choose the 2 cards you want to give to the scum```")
		
		give = pres.giveCards(scum,takeString,channel)
#could technically just have these 2 as 1 function only difference is the print statements
async def vpTrade(vp,sec,channel):
	take = False
	while(take == False):
		channel.send("```choose the card you want from the secretary```")
		takeString = await client.wait_for('message', check=lambda m: m.channel == channel and vp.user == m.author)
		take = vp.takeCards(sec,takeString,channel)
	give = False
	while(give == False):
		channel.send("```choose the card you want to give to the scum```")
		give = vp.giveCards(sec,takeString,channel)

#function that contains the game

async def mainScum(initialPlayerList,channel,client):
	
	deck.initDeck()#initialize the deck 
	playerList = []#initialize the list of players
	valid = 1
	#main loop and game logic for the game
	while(valid == 1):
		#the first time the game is ran, create the players and deal the deck
		if loop == 0:
			player1 = scumClasses.Player(initialPlayerList[0])
			player2 = scumClasses.Player(initialPlayerList[1])
			player3 = scumClasses.Player(initialPlayerList[2])
			player4 = scumClasses.Player(initialPlayerList[3])
			playerList = [player1,player2,player3,player4]
			deck.dealDeck(playerList)
			for player in playerList:
				player.sortCards()	#sort the deck to make it easier for the players,
				await player.user.send(player.hand)
		#if its not the first time then there should be trading between players
		else:
			
			deck.dealDeck(playerList)
			for player in playerList:
				player.sortCards()
				await player.user.send(player.hand)
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
			for player in playerList:
				player.sortCards()
				await player.user.send(player.hand)
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
		while playersLeft > 1:	#players with card left
		
			lastPlay = scumClasses.Play([])#the last hand played for checking if the played hand beats it
			#loop for setting status and players still left
			for player in playerList:
				if player.playStatus != 2:
					player.playStatus = 0#reset the players status for the next round
					playersIn += 1#players that havent skipped or finished
			await channel.send("```new round```")		
			while playersIn >1:	#while players are still in the round
				if player1.isTurn and player1.playStatus == 0:#if its the first players turn and they're still in, redundant as playstatus will never be 0 if its the players turn
					await channel.send('```' + player1.user.display_name+"'s turn```")		#make sure the user knows its their turn maybe better to have @user to make a discord notification
					validplay = False#for the loop checking if their play was valid
					
					#copy the pards into another list
					#the reason for this is because if the play isnt valid, we dont want lastPlaay to be overwritten since just having = makes nextLastPlay a pointer to lastPlay
					nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
					nextLastPlay.special = lastPlay.special
					#while the user hasn't sent a valid play
					while validplay == False:
						#inform the user how to send their play
						await channel.send('```type the cards you wish to play in the form of value suit, value suit and so on```')
						#wait for the users play and check if it is actually that user in the right channel
						userplay = await client.wait_for('message', check=lambda m: m.channel == channel and player1.user == m.author)
						#if the user skipped their turn, you can't skip on the very first turn
						if userplay.content == 'skip' or userplay.content == 'pass' and firstTurn == False:
							#make it so that the user is not in the round anymore and the players in is 1 less
							player1.playStatus = 1
							playersIn -= 1
						else:
							#call the function for playing the cards, this function converts the users string as well as checks if its valud
							nextLastPlay,validplay = await player1.playCards(userplay.content, firstTurn, nextLastPlay,channel)
							#if its not valid reset the last play, I think the resetting can go at the beginning of the while loop so that it saves 3 lines
							if validplay == False:
								await channel.send("```Please try again with a proper input```")
								nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
								nextLastPlay.special = lastPlay.special

					#now that its not the first turn set this to false, this will be set every loop, could put an if statement but it wouldnt improve runtime
					firstTurn = False
					#set the last play to be the temporary since it is valid
					lastPlay.cards = nextLastPlay.cards.copy()
					lastPlay.special = nextLastPlay.special
					await channel.send(f'```played: {lastPlay.cards}```')
					#if the player has 0 cards left
					if player1.playStatus == 2:
						#set their rank and then subtract based off of the number of players left, could also subtract and then do 4-players left
						player1.rank = 5-playersLeft
						#tell the player the position they finished
						await channel.send(f'```{player1.display_name} finished in position {player1.rank}```')
						playersLeft -=1
						#if theres only 1 player left theyre automatically scum
						if playersLeft == 1:
							if player2.playStatus == 0 or player2.playStatus == 1:
								player2.rank = 5-playersLeft
							elif player3.playStatus == 0 or player3.playStatus == 1:
								player3.rank = 5-playersLeft
							elif player4.playStatus == 0 or player4.playStatus == 1:
								player4.rank = 5-playersLeft
					#send the player their updating hand
					await player1.user.send(f'your hand is now: {player1.hand}')

					#if there is still a person in, set their turn as the next one
					#doesnt matter if the round finished since turns will be overwritten
					player1.isTurn = False
					if player2.playStatus == 0:
						player2.isTurn = True
					elif player3.playStatus == 0:
						player3.isTurn = True
					elif player4.playStatus == 0:
						player4.isTurn = True
					
					
				#almost exact copy of the previous if statement, the only difference is setting the turns
				#if I wanted to make it shorter I would use the playerlsit and a for loop so that it would be
				#if player.isTurn and player.playStatus == 0
				#then settting turns would be for i in len(playerList) if player[current user + i %4] set the turn same for rank
				#and you would keep track of the players index using index = index + 1 %4
				elif player2.isTurn and player2.playStatus == 0:
					await channel.send('```' + player2.user.display_name+"'s turn```")		#make sure the user knows its their turn maybe better to have @user to make a discord notification
					validplay = False#for the loop checking if their play was valid
					
					#copy the pards into another list
					#the reason for this is because if the play isnt valid, we dont want lastPlaay to be overwritten since just having = makes nextLastPlay a pointer to lastPlay
					nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
					nextLastPlay.special = lastPlay.special
					#while the user hasn't sent a valid play
					while validplay == False:
						#inform the user how to send their play
						await channel.send('```type the cards you wish to play in the form of value suit, value suit and so on```')
						#wait for the users play and check if it is actually that user in the right channel
						userplay = await client.wait_for('message', check=lambda m: m.channel == channel and player2.user == m.author)
						#if the user skipped their turn, you can't skip on the very first turn
						if userplay.content == 'skip' or userplay.content == 'pass' and firstTurn == False:
							#make it so that the user is not in the round anymore and the players in is 1 less
							player2.playStatus = 1
							playersIn -= 1
						else:
							#call the function for playing the cards, this function converts the users string as well as checks if its valud
							nextLastPlay,validplay = await player2.playCards(userplay.content, firstTurn, nextLastPlay,channel)
							#if its not valid reset the last play, I think the resetting can go at the beginning of the while loop so that it saves 3 lines
							if validplay == False:
								await channel.send("```Please try again with a proper input```")
								nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
								nextLastPlay.special = lastPlay.special
					#now that its not the first turn set this to false, this will be set every loop, could put an if statement but it wouldnt improve runtime
					firstTurn = False
					#set the last play to be the temporary since it is valid
					lastPlay.cards = nextLastPlay.cards.copy()
					lastPlay.special = nextLastPlay.special
					#if the play was valid send it in the main channel for people to see
					await channel.send(f'```played: {lastPlay.cards}```')
					#if the player has 0 cards left
					if player2.playStatus == 2:
						#set their rank and then subtract based off of the number of players left, could also subtract and then do 4-players left
						player2.rank = 5-playersLeft
						#tell the player the position they finished
						await channel.send(f'```{player2.display_name} finished in position {player2.rank}```')
						playersLeft -=1
						if playersLeft == 1:
							if player3.playStatus == 0 or player3.playStatus == 1:
								player3.rank = 5-playersLeft
							elif player4.playStatus == 0 or player4.playStatus == 1:
								player4.rank = 5-playersLeft
							elif player1.playStatus == 0 or player1.playStatus == 1:
								player1.rank = 5-playersLeft
					
					await player2.user.send("your hand is now: ")
					await player2.user.send(player2.hand)
					
					player2.isTurn = False
					if player3.playStatus == 0:
						player3.isTurn = True
					elif player4.playStatus == 0:
						player4.isTurn = True
					elif player1.playStatus == 0:
						player1.isTurn = True



				elif player3.isTurn and player3.playStatus == 0:
					await channel.send('```' + player3.user.display_name+"'s turn```")		#make sure the user knows its their turn maybe better to have @user to make a discord notification
					validplay = False#for the loop checking if their play was valid
					
					#copy the pards into another list
					#the reason for this is because if the play isnt valid, we dont want lastPlaay to be overwritten since just having = makes nextLastPlay a pointer to lastPlay
					nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
					nextLastPlay.special = lastPlay.special
					#while the user hasn't sent a valid play
					while validplay == False:
						#inform the user how to send their play
						await channel.send('```type the cards you wish to play in the form of value suit, value suit and so on```')
						#wait for the users play and check if it is actually that user in the right channel
						userplay = await client.wait_for('message', check=lambda m: m.channel == channel and player3.user == m.author)
						#if the user skipped their turn, you can't skip on the very first turn
						if userplay.content == 'skip' or userplay.content == 'pass' and firstTurn == False:
							#make it so that the user is not in the round anymore and the players in is 1 less
							player3.playStatus = 1
							playersIn -= 1
						else:
							#call the function for playing the cards, this function converts the users string as well as checks if its valud
							nextLastPlay,validplay = await player3.playCards(userplay.content, firstTurn, nextLastPlay,channel)
							#if its not valid reset the last play, I think the resetting can go at the beginning of the while loop so that it saves 3 lines
							if validplay == False:
								await channel.send("```Please try again with a proper input```")
								nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
								nextLastPlay.special = lastPlay.special

					#now that its not the first turn set this to false, this will be set every loop, could put an if statement but it wouldnt improve runtime
					firstTurn = False
					#set the last play to be the temporary since it is valid
					lastPlay.cards = nextLastPlay.cards.copy()
					lastPlay.special = nextLastPlay.special
					await channel.send(f'```played: {lastPlay.cards}```')
					#if the player has 0 cards left
					if player3.playStatus == 2:
						#set their rank and then subtract based off of the number of players left, could also subtract and then do 4-players left
						player3.rank = 5-playersLeft
						#tell the player the position they finished
						await channel.send(f'```{player3.display_name} finished in position {player3.rank}```')
						playersLeft -=1
						if playersLeft == 1:
							if player4.playStatus == 0 or player4.playStatus == 1:
								player4.rank = 5-playersLeft
							elif player1.playStatus == 0 or player1.playStatus == 1:
								player1.rank = 5-playersLeft
							elif player2.playStatus == 0 or player2.playStatus == 1:
								player2.rank = 5-playersLeft
					await player3.user.send("your hand is now: ")
					await player3.user.send(player3.hand)
					
					player3.isTurn = False
					if player4.playStatus == 0:
						player4.isTurn = True
					elif player1.playStatus == 0:
						player1.isTurn = True
					elif player2.playStatus == 0:
						player2.isTurn = True
					#if third automatically assign rank 3 and 4 at the same time

				elif player4.isTurn and player4.playStatus == 0:
					await channel.send('```' + player4.user.display_name+"'s turn```")		#make sure the user knows its their turn maybe better to have @user to make a discord notification
					validplay = False#for the loop checking if their play was valid
					
					#copy the pards into another list
					#the reason for this is because if the play isnt valid, we dont want lastPlaay to be overwritten since just having = makes nextLastPlay a pointer to lastPlay
					nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
					nextLastPlay.special = lastPlay.special
					#while the user hasn't sent a valid play
					while validplay == False:
						#inform the user how to send their play
						await channel.send('```type the cards you wish to play in the form of value suit, value suit and so on```')
						#wait for the users play and check if it is actually that user in the right channel
						userplay = await client.wait_for('message', check=lambda m: m.channel == channel and player4.user == m.author)
						#if the user skipped their turn, you can't skip on the very first turn
						if userplay.content == 'skip' or userplay.content == 'pass' and firstTurn == False:
							#make it so that the user is not in the round anymore and the players in is 1 less
							player4.playStatus = 1
							playersIn -= 1
						else:
							#call the function for playing the cards, this function converts the users string as well as checks if its valud
							nextLastPlay,validplay = await player4.playCards(userplay.content, firstTurn, nextLastPlay,channel)
							#if its not valid reset the last play, I think the resetting can go at the beginning of the while loop so that it saves 3 lines
							if validplay == False:
								await channel.send("```Please try again with a proper input```")
								nextLastPlay = scumClasses.Play(lastPlay.cards.copy())
								nextLastPlay.special = lastPlay.special


					#now that its not the first turn set this to false, this will be set every loop, could put an if statement but it wouldnt improve runtime
					firstTurn = False
					#set the last play to be the temporary since it is valid
					lastPlay.cards = nextLastPlay.cards.copy()
					lastPlay.special = nextLastPlay.special
					await channel.send(f'```played: {lastPlay.cards}```')
					#if the player has 0 cards left
					if player4.playStatus == 2:
						#set their rank and then subtract based off of the number of players left, could also subtract and then do 4-players left
						player4.rank = 5-playersLeft
						#tell the player the position they finished
						await channel.send(f'```{player4.display_name} finished in position {player4.rank}```')
						playersLeft -=1
						if playersLeft == 1:
							if player1.playStatus == 0 or player1.playStatus == 1:
								player1.rank = 5-playersLeft
							elif player2.playStatus == 0 or player2.playStatus == 1:
								player2.rank = 5-playersLeft
							elif player3.playStatus == 0 or player3.playStatus == 1:
								player3.rank = 5-playersLeft
					await player4.user.send("your hand is now: ")
					await player4.user.send(player4.hand)
					
					player4.isTurn = False
					if player1.playStatus == 0:
						player1.isTurn = True
					elif player2.playStatus == 0:
						player2.isTurn = True
					elif player3.playStatus == 0:
						player3.isTurn = True
					#if third automatically assign rank 3 and 4 at the same time
			
		#check if the users want to play another round
		await channel.send("play another round?")
		#it shouldnt matter who says no
		response = await client.wait_for('message')
		if (response == 'no'):
			valid = 0