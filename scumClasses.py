#This file contains the helper functions and classes for the main scum program
#This file wont have any user itneraction

#Khem Holden started 1/2/2019
from random import shuffle
from collections import deque
from enum import Enum
import discord

#enum for holding the suit
#suit value doesn't actually matter, this is just easier for creating the deck of cards
class CardSuit(Enum):
	Hearts = 1
	Diamonds = 2
	Spades = 3
	Clubs = 4
#enum for holding the value of the cards
#two is the high card 3 is the low card
class CardValue(Enum):
	Three = 1
	Four = 2
	Five = 3
	Six = 4
	Seven = 5
	Eight = 6
	Nine = 7
	Ten = 8
	Jack = 9
	Queen = 10
	King = 11
	Ace = 12
	Two = 13
	#enum already suports an == but not < or > so these have to be provided
	def __lt__(self,other):
		if self.__class__ is other.__class__:
			return self.value < other.value
		else:
			print("values are not of the same type")
	def __gt__(self,other):
		if self.__class__ is other.__class__:
			return self.value > other.value
		else:
			print("values are not of the same type")
#dictionarys for converting the user string to a card class
cardValDict = {'3':CardValue.Three, 'three':CardValue.Three, '4':CardValue.Four, 'four':CardValue.Four, '5':CardValue.Five, 'five':CardValue.Five,
	'6':CardValue.Six, 'six':CardValue.Six, '7':CardValue.Seven, 'seven':CardValue.Seven, '8':CardValue.Eight, 'eight':CardValue.Eight, '9':CardValue.Nine,
	'nine':CardValue.Nine, '10':CardValue.Ten, 'ten':CardValue.Ten, 'j':CardValue.Jack, 'jack':CardValue.Jack, 'q':CardValue.Queen, 'queen':CardValue.Queen,
	'k':CardValue.King, 'king':CardValue.King, 'a':CardValue.Ace, 'ace':CardValue.Ace, '2':CardValue.Two, 'two':CardValue.Two}
cardSuitDict = {'h':CardSuit.Hearts, 'hearts':CardSuit.Hearts, 'd':CardSuit.Diamonds, 'diamonds':CardSuit.Diamonds, 's':CardSuit.Spades, 'spades':CardSuit.Spades, 'c':CardSuit.Clubs, 'clubs':CardSuit.Clubs}

#class for the card itself
class Card:
	#creating a card requires a value and a suit
	def __init__(self, value, suit):
		self.value = value
		self.suit = suit
	#whenever you want to print a card, print it in a format users can read instead of the object pointer
	def __repr__(self):
		cardstring = str(str(self.value.name) + ' of ' + str(self.suit.name))
		return cardstring
	#if the cards are equal their suit and value will be the same
	def __eq__(self,comparing):
		return self.value == comparing.value and self.suit == comparing.suit
	#if a card is greater than or less than, their value will be compared
	def __lt__(self,other):
		if self.__class__ is other.__class__:
			return self.value < other.value
		else:
			print("card variables are not of the same type")
	def __gt__(self,other):
		if self.__class__ is other.__class__:
			return self.value > other.value
		else:
			print("card variables are not of the same type")
	#only used for sorting the cards, the value isn't used anywhere else because you can just use card.value
	#would matter if encapsulation was implemented
	def getValue(Card):
		return Card.value

#the class for the deck of cards, this is just used for creating and dealing the deck, it shouldn't get used outside of that
class Deck:
	#initialize the deck as an empty queue
	def __init__(self):
		self.deck = deque([])
	#creates the cards in the deck and shuffles the deck
	#need this second init because the main game loop doesnt reuse cards when a user plays it, they just get deleted
	def initDeck(self):
		x,y = 1,1
		for suit in range(1,5):
			for value in range(1,14):
				self.deck.append(Card(CardValue(value),CardSuit(suit)))
		#shuffle the deck twice, just because, uses the built in queue shuffle function
		shuffle(self.deck)
		shuffle(self.deck)
	#deal deck to all players in the list
	def dealDeck(self,playerList):
		#make sure that the deck is dealth evenly between all players, there should only ever be 4 players
		#fucntion will cause an error if the playerList is ever not a factor of 52
		for z in range(0,52//len(playerList)):#need the // for keeping it as an int
			for player in playerList:
				player.hand.append(self.deck.popleft())

#class for the player itself
class Player:
	#initialize all the variables the player has
	def __init__(self, user):  
		self.user = user
		self.isTurn = False	#order is turn order
		self.playStatus = 0		#playstatus is 0= has a hand 1= skipped 2= done
		self.rank = 0			#1 = president, 2 = vice president, 3 = secretary, 4 = scum initially no one has a rank
		self.hand = []			#hands are initially empty
	#in cae theres ever a print(player)
	def __repr__(self): 
		return self.user.display_name
	#sort the cards in the users hand
	def sortCards(self):
		self.hand.sort(key =Card.getValue)
	#function for translating the users input into a an array of cards that the program can actually use
	def userStringTranslate(self,userString):
		#set the whole string to lowercase to save lines if the user ever has random capital letters
		userString = userString.lower()
		userStringArray = userString.split(',')#tokenize the string based on commas
		inputArray = []#the array that will store the cards from the user input
		print(userStringArray)
		for card in userStringArray:
			if len(card) == 0:
				return inputArray
		for i in range(len(userStringArray)):
			#tokenize the string based on spaces since user input should be something like 3 of clubs
			tokenString = userStringArray[i].split(' ')

			if(len(tokenString) != 0):
				
				if(len(tokenString[0]) != 0 and len(tokenString) >1):#in case the user puts a space after a , like proper english
					CardArray = [cardValDict.get(tokenString[0]),cardSuitDict.get(tokenString[-1])]#use the first an last part of the string, avoids anything in between like of in 3 of clubs
					inputCard = Card(CardArray[0],CardArray[1])
					inputArray.append(inputCard)#add the card to the array of cards
					#dont actually need the == part
				elif(len(tokenString[0]) != 0 and (len(tokenString) == 1)):
					value = cardValDict.get(tokenString[0])

					for tempCard in self.hand:
						if(tempCard.value.value == value.value and tempCard not in inputArray):
							inputCard = tempCard
							inputArray.append(inputCard)#add the card to the array of cards
							break
					#create a card just so that it has a temp one then later when it checks if its in hand itll be false
					if 'inputCard' not in locals():
						inputCard = Card(CardValue(value),CardSuit(1))
						inputArray.append(inputCard)
					else:
						if (inputCard.value.value !=tempCard.value.value):
							inputCard = Card(CardValue(inputCard.value.value),CardSuit(1))
							inputArray.append(inputCard)
					print(inputCard)
				elif(len(tokenString) == 2 and (len(tokenString[0]) == 0)):
					value = cardValDict.get(tokenString[1])
					for tempCard in self.hand:
						if(tempCard.value.value == value.value and tempCard not in inputArray):
							inputCard = tempCard
							inputArray.append(inputCard)#add the card to the array of cards
							break
					#create a card just so that it has a temp one then later when it checks if its in hand itll be false
					if 'inputCard' not in locals():
						inputCard = Card(CardValue(value),CardSuit(1))
						inputArray.append(inputCard)
					else:
						if (inputCard.value.value !=tempCard.value.value):
							inputCard = Card(CardValue(inputCard.value.value),CardSuit(1))
							inputArray.append(inputCard)
					print(inputCard)
				else:
					CardArray = [cardValDict.get(tokenString[1]),cardSuitDict.get(tokenString[-1])]#if the first value is a space then use the next one
					inputCard = Card(CardArray[0],CardArray[1])
					inputArray.append(inputCard)#add the card to the array of cards
		return inputArray
	#fucntion for processing the user string and then checking if its valid
	async def playCards(self, userString, firstTurn, lastPlay,channel):
		#translate the input string
		inputArray = self.userStringTranslate(userString)
		#if the play is valid by having all the cards in your hand
		#could just use not all() and replace pass with the else contents
		if(all(elem in self.hand for elem in inputArray)):
			pass
		else:
			await channel.send("```at least 1 card isn't in your hand```")
			return lastPlay,False
			
		#make the play a play class and then use the is valid function
		play = Play(inputArray)
		#if the play was falid
		if(play.validPlay(firstTurn, lastPlay)):
			#remove the cards in hand
			for elem in inputArray:
				self.hand.remove(elem)
			#if there are no cards left then the player is done
			if len(self.hand) == 0:
				self.playStatus = 2

			return play,True
		else:

			return lastPlay,False
	#function for taking cards used for trading at the start of rounds
	async def takeCards(self,Player,userInput,channel):
		#translate the cards the user wants to take into a string different translate for this fucntion for ease on the pres/vp just getting a vlue not the exact card
			
		takeCards = self.userStringTranslate(userInput)
		#check to see if the user is taking the right amount of cards
		#pres takes 2 secretary takes 1
		if(not(self.rank == 1 and len(takeCards) == 2) and not(self.rank == 2 and len(takeCards) == 1)):
			await channel.send('please enter the proper amount of cards to take')
			return False
			#could make this return a number so the channel.send is never in this file and youd send the string based on the return number
		#check if the cards are in the hand of the player that you are taking from
		for card in takeCards:
			if(card not in Player.hand):
				await channel.send(f'{card} not in {player.user.display_name}s hand')
				return False
		#remove the card from the player ad add it to your hand
		for card in takeCards:
			self.hand.append(card)
			Player.hand.remove(card)
		return True	
	#function for giving cards used for trading at the start of rounds
	#basically the same as the previous fucntion but with the remove/appends swapped
	async def giveCards(self,Player,userInput,channel):
		giveCards = self.userStringTranslate(userInput)
		if(not(self.rank == 1 and len(giveCards) == 2) and not(self.rank == 2 and len(giveCards) == 1)):
			await channel.send('please enter the proper amount of cards to give')
			return False
		for card in giveCards:
			if(card not in Player.hand):
				await channel.send(f'{card} not in {player.user.display_name}s hand')
				return False
		for card in giveCards:
			self.hand.remove(card)
			Player.hand.append(card)
		return True	

#class for playing the cards mainly just used for checking if its valid
class Play:
	#initialize the class with the cards to play
	def __init__(self,cards):
		self.cards = cards
		self.special = 0
	#main function for checking if the cards is a special type
	#bombs, poisons and spikes are special
	#bombs are straight of doubles 3,3,4,4,5,5 is an example
	#poisons are 4 of a kind
	#spikes are 2 consecutive triples 3,3,3,4,4,4
	def isSpecial(self):
		#if loop for checking if theres a bombs
		#simpler way to do this would be if len(self.cards)>=6 and len(self.cards)%2 == 0
		#then for loop for checking if each pair is actually a pair and a straight
		if len(self.cards) >= 6:
			#if the first 2 cards are a pair
			if self.cards[0].value == self.cards[1].value:
				#if the third card is consecutive from the first pair have the %2 here because if it was before then it would ignore spikes
				if self.cards[0].value.value +1 == self.cards[2].value.value and len(self.cards)%2 == 0:
					#if the second pair is actually a pair
					if self.cards[2].value == self.cards[3].value:
						#if the fifth card is consecutive from the second pair
						if self.cards[2].value.value +1 == self.cards[4].value.value:
							#if the third pair is actually a pair
							if self.cards[4].value == self.cards[5].value:
								#if there are more than 6 cards the rest of this is the same if/elses as before just with the next pairs
								if len(self.cards) >6:
									if self.cards[4].value.value +1 == self.cards[6].value.value:
										if self.cards[6].value == self.cards[7].value:
											if len(self.cards) >8:
												if self.cards[6].value.value +1 == self.cards[8].value.value:
													if self.cards[8].value == self.cards[9].value:
														if len(self.cards) > 10:
															if self.cards[8].value.value +1 == self.cards[10].value.value:
																if self.cards[10].value == self.cards[11].value:
																	if len(self.cards) > 12:
																		self.special = 0
																	else:
																		self.special = 1
																else:
																	self.special = 0
															else:
																self.special = 0
														else:
															self.special = 1
													else:
														self.special = 0
												else:
													self.special = 0
											else:
												self.special = 1
										else:
											self.special = 0
									else:
										self.special = 0
								else:
									self.special = 1
							else:
								self.special = 0
					else:
						self.special = 0
				#if the first 3 cards are a triple
				elif self.cards[0].value == self.cards[1].value == self.cards[2].value and len(self.cards)%3 == 0:
					#if the next triple is consecutive
					if self.cards[0].value.value + 1 == self.cards[3].value.value:
						#if the next triple is actually a triple
						if self.cards[3].value == self.cards[4].value and self.cards[3].value == self.cards[5].value:
							#smae as the previous logic just with the next triples
							if len(self.cards) > 6:
								if self.cards[3].value.value + 1 == self.cards[6].value.value:
									if self.cards[6].value == self.cards[7].value == self.cards[8].value:
										if len(self.cards) > 9:
											if self.cards[6].value.value + 1 == self.cards[9].value.value:
												if self.cards[9].value == self.cards[10].value == self.cards[11].value:
													if len(self.cards) > 12:
														self.special = 0
													else:
														self.special = 3
														
												else:
													self.special = 0
											else:
												self.special = 0
										else:
											self.special = 3
									else:
										self.special = 0
								else:
									self.special = 0
							else:
								self.special = 3
						else:
							self.special = 0
					else:
						self.special = 0
				else:
					self.special = 0
			else:
				self.special = 0
		#if theres 4 cards and theyre all equal
		elif len(self.cards) == 4:
			if self.cards[0].value == self.cards[1].value and self.cards[0].value == self.cards[2].value and self.cards[0].value == self.cards[3].value:
				self.special = 2
			else:
				self.special = 0
	#function for checking if the play is valid
	def validPlay(self,firstTurn, lastHand):
		#if the play is special
		self.isSpecial()
		print(lastHand.cards)
		print(self.cards)
		if len(lastHand.cards) == 0:#only happens on a new round
			#set the last play to be full of threes to have something to compare so there arent any additional checks for first turn, this only affects straight logic
			for x in range(0, len(self.cards)):
				lastHand.cards.append(Card(CardValue.Three,CardSuit.Clubs))
		#three of clubs is the starting card

		#if it is the first turn then the three of clubs should be in the hand
		if firstTurn == True:
			if (Card(CardValue.Three,CardSuit.Clubs)) not in self.cards:
				return False
		
		if lastHand.special > 0 or self.special > 0:#if the last hand was a special play this one has to be
			if self.special > lastHand.special: #if you have a higher special play
				return True
			#if your specials are the same but yours has a higher or equal card
			elif self.special == lastHand.special and (self.cards[-1].value > lastHand.cards[-1].value or self.cards[-1].value == lastHand.cards[-1].value):
				return True
			else:
				return False
		else:
			straight = False 	#flag for if the play is a straight

			if len(lastHand.cards) == 1:#single
				#if the single is greater than or equal to then its a valid single
				if len(self.cards) == 1 and (self.cards[0].value > lastHand.cards[0].value or self.cards[0].value == lastHand.cards[0].value):#check to make sure theres only 1 card
					return True
				else:
					return False
				
			elif len(lastHand.cards) == 2:#double
				#if the double is greater than or equal to then its a valid double
				if len(self.cards) == 2 and self.cards[0].value == self.cards[1].value and (self.cards[0].value > lastHand.cards[0].value or self.cards[0].value == lastHand.cards[0].value): #check if right number of cards amd if its a pair
					return True
				else:
					return False
				
			elif len(lastHand.cards) == 3:#triple or straight
				#if the triple is greater than the last triple
				if(lastHand.cards[0].value == lastHand.cards[1].value):	#check if straight only check two cards because assumption that this next code will work
					if len(self.cards) == 3 and self.cards[0].value == self.cards[1].value == self.cards[2].value and (self.cards[0].value > lastHand.cards[0].value or self.cards[0].value == lastHand.cards[0].value):
						return True
					elif firstTurn == True:
						straight = True
					elif lastHand.cards[0].suit == lastHand.cards[1].suit:
						straight = True
					else:

						return False
				
				else:	#if last hand was 3 cards and isnt a triple
					straight = True

				
			else: #straights
				straight = True
		#if there is a straight
		if straight == True:
			#for each card in the straight
			if len(self.cards)<3:
				return False
			for x in range(0,len(self.cards)-1):
				#cheack if the next card is consecutive
				if self.cards[x].value.value +1 != self.cards[x+1].value.value:
					print("not consecutive")
					return False
			if self.cards[-1].value > lastHand.cards[-1].value or self.cards[-1].value == lastHand.cards[-1].value:

				return True
			else:
				print("not high enough")
				return False
			