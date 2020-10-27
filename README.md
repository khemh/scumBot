base program for implementing a version of scum aka president in discord
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

#TODO LIST
#proper error handling eg:send the problem with the users play in the channel, for example straight isnt consecutive
#make it so that if there are more than 4 people who want to play then the scum gets switched out for them
#make it so that players can rearrange cards in their hand
#multithread trading
#minor changes to user interaction
