import socket
import sys
import pickle
from card_vars import ranks, suits, card, deck, deck_dealing, decl_values, card_vals, hierarchy_
from random import choice, shuffle 
from itertools import chain
import threading
import time
import re


# Team scores
score = {'team_1': 0, 'team_2': 0}

 
ranks = [str(i) for i in range(7, 11)] + 'J, Q, K, A'.split(', ')
suits = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
card = namedtuple('card', ['Rank', 'Suit'])
deck = [card(rank, suit) for rank in ranks for suit in suits]


def checkDeclValidity(declaration):
    """Checks if declaration is made out of card ranks and suits. Returns 1 if all checks passed and None otherwise."""
    
    # check 2. Number of items in each declaration should be a whole number (each declaration is made of n cards and 
    # each card is made up of two components: rank and suit so n * 2 is a whole number regardless of n). If number is 
    # odd return None and prompt user for input again
    if len(re.split(',*\s', ', '.join(re.split('\sand\s', declaration)))) % 2 != 0:
        return None

    # check 3. Check each card is made up of valid ranks
    for i in re.split(',*\s', ', '.join(re.split('\sand\s', declaration)))[0::2]:
        if i not in ranks:
            return None
        
    # check 4. Check each card is made up of valid suits
    for j in re.split(',*\s', ', '.join(re.split('\sand\s', declaration)))[1::2]:
        if j not in suits:
            return None
    
    print('passed all checks in decl validity')
    
    return 1

def tryInputAgain(message, player):
    declaration = input(f'{message}. Try again:\n')
    
    while check_decl_validity(declaration) != 1:
        declaration = input('Try again?\n')
    
    for i in re.split('\sand\s', declaration):
        declarations = [[Card(j, k) for j, k in zip(re.split(',*\s', i)[0::2], re.split(',*\s', i)[1::2])]]
        
        if declaration == 'none':
            return 'none'
        else:
            return declarations


def declarationChecks(declarations, hand, trump_suit):
    
    """
    There are 3 things to consider when looking at declarations:

    1. Does the declaration consist of cards that the player actually holds?
    2. Does the declaration actually form a sequence?
    3. Do any cards in multiple declarations overlap?

    If the answer to any of the above questions is NO then the function will return None.
    """
    
    # Check 1
    print(declarations)
    if declarations == [] or declarations == ['none']:
        return 1
    
    hand.sort(key=lambda x: (x[1], hierarchy_[x[0]]))
    print(hand)
    
    for j in declarations:    
        j.sort(key=lambda x: (x[1], hierarchy_[x[0]]))
        if not set(j).issubset(hand):
            return 'Declaration not in hand'
    
    print('check #1 passed\n')

    # Check 2    
    for j in declarations:
        
        bingo = 0 #Keeps track of how many pairs of cards have matching suits and are part of a sequence
            
        # Cartbelote ****** DONE ******
        if j == [card(Rank = 'Q', Suit = trump_suit), card(Rank = 'K', Suit = trump_suit)]:
            print(f'{j} is Cartbelote')
            continue
        
        # Square (four cards of identical rank) ****** DONE ******       
        elif len(j) == 4:
            if not False in [True if m[0] == j[-1][0] and m[1] != j[-1][1] else False for m in j[:-1]]:
                 print(f'{j} is a square')
                 continue
        
        # sequence of 3+ cards ****** DONE ******
        else:
        
            for k in range(1, len(j)): #we don't start at index 0 because there are no predecessors to it, i.e. no cards to be compared

                # if suit of card i matches that of card i-1

                if j[k][1] == j[k-1][1]:
                    print('Comparing cards: ({0}, {1})'.format(hand[k], hand[k - 1]))
                    print('k value is: {}'.format(k))

                    # if card i is 1 step above card i-1 in hierarchy, e.g. 'J' is 1 step above '10'
                    if hierarchy_[j[k][0]] - hierarchy_[j[k-1][0]] == 1: 
                        bingo += 1 #add 1 tick to bingo
                        print('bingo + 1 = {}'.format(bingo))

                        # at the last card check if we have 2+ bingos
                        if k == len(j) - 1:
                            if bingo >= 2: 
                                print('\nFOUND SEQUENCE! \n {}\n'.format(j[-1: -1 - bingo - 1:-1]))
                                print('*' * 40)

                            else:
                                print('Not a valid declaration')
                                return None                        

                #if card i and i-1 suits don't match check how many bingos did we get up to card i-1. 
                else:
                    print('Not a valid declaration')
                    return f'Declaration {j} is not a valid sequence'
                
    print('passed check #2')
    
    # Check 3    
    counter = 1
    
    for i in declarations:

        if declarations.index(i) != 0: #skip first declaration as there are no previous declarations to compare it to
            while declarations.index(i) >= counter:

                for j in i:
                    if j == card(Rank='Q', Suit=trump_suit) or j == card(Rank='K', Suit=trump_suit): # ignore cartbelote cards
                        continue
                    elif j in declarations[declarations.index(i) - counter]: # check if card is in previous declaration
                        return 'card {} from declaration {} in another declaration {}'.format(j, i, declarations[player][declarations[player].index(i) - counter])

                counter += 1 # increment counter by one so we can gradually check all previous declarations for instances of card j

            counter = 1 # reset counter before moving on to checking duplicate cards in the next declaration
            
    print('passed check #3')
    
    return 1 # if the declaration passes all checks exit the function with True 
        
    
def resetCopyDeck():
    """
    Resets the card deck if we need to deal out cards again. Only happens if no one picks a trump suit
    """
    deck_dealing = deck[:]
    
def choicePop():
    """
    Picks a random card from the decks and pops it from the deck list
    """
    card = choice(deck_dealing)
    deck_dealing.pop(deck_dealing.index(card))
    return card

def checkBela(decl_dict, trump):
    """
    Bela is always a valid declaration, i.e. the player who holds it gets 20 points regardless of the other team's declarations.
    This function scans both team's declarations for Bela. If one is found this function removes the Bela from the decl_dict before
    it feeds into the declComp() function. It also calls the score function which gives the team who holds Bela 20 points.
    """

    global score
    
    bela = [card(Rank='Q', Suit=trump), card(Rank='K', Suit=trump)]

    for client, decl in decl_dict.items():        
       
        if bela in decl:
            # Add 20 points to the team holding Bela
            for team, team_members in teams.items():
                if client in team_members:
                    score[team] += 20
                    break
            print(f'{client} has declared Bela. {team} gets +20 points!')
        
            # Remove Bela from decl_dict (decl_dict will be used in declCompare which doesn't need a declaration that 
            # is always valid (just like Bela) hence why it is removed)
            decl.pop(decl.index(bela))  
            break
        
    return decl_dict

def checkAnyDecl(decl_dict):
    """
    Checks if decl_dict contains any declarations. Returns 1 if at least one declaration exists and 0 otherwise. 
    To be used after checkBela()
    """
    return 0 if len(list(filter(None, chain.from_iterable(decl_dict.values())))) == 0 else 1

def flatListFromDictVal(decl_dict, key_list):
    """
    Takes a declaration dict and flattens its values into one list. Useful when dicts have nested lists as values.
    """
    return list(filter(None, chain.from_iterable([decl_dict[key] for key in key_list])))

def flatListMatrix(decl_flat_list, trump):
    """
    
    """             
    return [f'{declType(decl)}{declLen(decl)}{hierarchy_[decl[-1].Rank]}{int(decl[-1].Suit == trump)}' for decl in decl_flat_list]

def declToString(decl):
    """
    Converts a declaration from list of named tuples to string 
    """
    empty_string = ''

    for card in decl:
        if card != decl[-1]:
            empty_string += card[0] + ', '
        else:
            empty_string += card[0]
    
    return empty_string

def firstRoundHand(trump_card):
    """
    First round hand. Players are dealt 5 cards each
    """
    #Get rid of the trump card from the deck before dealing out the cards to avoid duplicates
    deck_dealing.pop(deck.index(trump_card))
    return [[choicePop() for i in range(5)] for i in range(4)]

def secondRoundHand():
    """
    Second round hand. After trump suit is chosen, players are dealt 3 cards each (one player gets 2 cards + trump card)
    """
    return [[choicePop() for i in range(3)] for i in range(3)], deck_dealing
    
def declLen(declaration):
    """
    Returns the length of the declaration. If the declaration is a sequence with more than 5 cards the function will return 5.
    """
    if declType(declaration) == 1 and len(declaration) > 5:
        return 5
    else:
        return len(declaration)

def declType(declaration):
    """
    There are 3 tiers of declarations:
    tier 1 (lowest): Sequences. E.g. J, Q, K, A
    tier 2: Squares. E.g. Q, Q, Q, Q
    tier 3 (highest, i.e. declaration always counts): Bela. Only trump suit Q, K
    """
    
    # If the length of declaration is 2 then it can only be a Bela
    if len(declaration) == 2:
        return 3
    # If the length of declaration is 4 it can either be a sequence or a square. The following code checks that:
    if len(declaration) == 4: 
        for card in declaration[1:]:
            if card.Rank == declaration[declaration.index(card) - 1].Rank:
                pass
                if card == declaration[-1]:
                    return 2
            else: 
                return 1
    else:
        return 1

def declMax(decl_dict, trump):
    """
    Returns the name of the team with the highest value declaration or zero if there is a tie between the max declarations of each team
    """
    
    flat_t1 = flatListMatrix(flatListFromDictVal(decl_dict, teams['team_1']), trump)
    flat_t2 = flatListMatrix(flatListFromDictVal(decl_dict, teams['team_2']), trump)
    
    t1, t2 = max(flat_t1), max(flat_t2)
    
    if (t1, t2).count(max(t1, t2)) != 1:
        return 0
    else:
        return list(teams.keys())[(t1, t2).index(max(t1, t2))]


# def greeting(conn_):
#     print('receiving thread has started')
    
#     conn_.send(pickle.dumps('Welcome to the server. Waiting for other player to join') + b'|')


def dealCards(clients):
    
    """
    Messages are separated by b'|'
    """
    
    all_data = b''    
    
    # stage 1. deal cards and pick trump suit 
    trump = ''
    
    #rand_trump = choice(deck_dealing)
    rand_trump = card(Rank='A', Suit='Hearts')
    print(f'rand_trump is {rand_trump}')
       
    first_hand = [[card(Rank='7', Suit='Hearts'), card(Rank='8', Suit='Hearts'), card(Rank='9', Suit='Hearts'), card(Rank='10', Suit='Hearts'), card(Rank='J', Suit='Hearts')],
                 [card(Rank='7', Suit='Clubs'), card(Rank='8', Suit='Clubs'), card(Rank='9', Suit='Clubs'), card(Rank='10', Suit='Clubs'), card(Rank='J', Suit='Clubs')],
                 [card(Rank='7', Suit='Spades'), card(Rank='8', Suit='Spades'), card(Rank='9', Suit='Spades'), card(Rank='10', Suit='Spades'), card(Rank='J', Suit='Spades')],
                 [card(Rank='7', Suit='Diamonds'), card(Rank='8', Suit='Diamonds'), card(Rank='9', Suit='Diamonds'), card(Rank='10', Suit='Diamonds'), card(Rank='J', Suit='Diamonds')]]
    #first_hand = firstRoundHand(rand_trump)
    
    client_hand_dict = {}
    
    print('first_hand to debug:\n', first_hand)
    
    for client, hand in zip(clients, first_hand):
        client_hand_dict[client] = hand
        client.sendall(pickle.dumps({'hand 1': hand}) + b'|')
        print('sent hand')
        client.sendall(pickle.dumps({'rand_trump': rand_trump}) + b'|')
        print('sent rand_trump')       
    
    # players chose whether to play randomly chosen trump suit                   
    for client in clients:
        client.sendall(pickle.dumps({'pick_trump': 1}) + b'|')
        print(f'client {client}\'s turn to pick trump')
        
        while 1:
            data = client.recv(1024)
            all_data += data
            
            if data and b'|' in all_data:
                to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
                print(to_analyse)
                all_data = all_data[all_data.index(b'|') + 1:]
                
                if to_analyse == 'play' or to_analyse == rand_trump[1]:
                    trump = rand_trump[1]
                    trump_client = client 
                    print(f'{client} picked trump suite: {trump}')
                    for i in clients:
                        i.sendall(pickle.dumps(f'client {client} has picked trump suit {trump}') + b'|')
                        i.sendall(pickle.dumps({'trump': trump}) + b'|')

                    # if trump suit is picked deal the second round of cards (3 cards to each player)
                    
                    #second_hand = secondRoundHand()
                    
                    secondee = [[card(Rank='Q', Suit='Diamonds'), card(Rank='K', Suit='Diamonds'), card(Rank='A', Suit='Diamonds')],
                               [card(Rank='Q', Suit='Spades'), card(Rank='K', Suit='Spades'), card(Rank='A', Suit='Spades')],
                               [card(Rank='Q', Suit='Clubs'), card(Rank='K', Suit='Clubs'), card(Rank='A', Suit='Clubs')]]
                    second_hand = secondee, [card(Rank='Q', Suit='Hearts'), card(Rank='K', Suit='Hearts')]
                    
                    client_hand_dict[client] += second_hand[1] + [rand_trump]
                    client.send(pickle.dumps({'hand 2': client_hand_dict[client]}) + b'|')
                    
                      
                    for j, k in zip([l for l in clients if l != client], second_hand[0]):
                        client_hand_dict[j] += k
                        # send the cards to each player
                        j.send(pickle.dumps({'hand 2': client_hand_dict[j]}) + b'|')
                            
                    return tricks(clients, trump, trump_client, client_hand_dict)
                    #return declInput(clients, trump, trump_client, client_hand_dict)
                else: 
                    break

    
    # if all players pass on the random trump suit, free for all 
    if not trump:
        for client in clients:
            client.send(pickle.dumps({'pick_trump': 2}) + b'|')
            [i.send(pickle.dumps(f'client {client} turn to declare') + b'|') for i in clients if i != client]
            while 1:
                data = client.recv(1024)
                all_data += data
            
                if data and b'|' in all_data:
                    to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
                    print(to_analyse)
                    all_data = all_data[all_data.index(b'|') + 1:]
                    if pickle.loads(data) in suits:
                        trump = pickle.loads(data)
                        trump_client = client
                        for i in clients:
                            i.sendall(pickle.dumps(f'client {client} has picked trump suit {trump}') + b'|')
                            i.sendall(pickle.dumps({'trump': trump}) + b'|')
                        
                        break                     
                    
                    # when all players pass on picking a trump suit deal the cards again. **** Next player needs to deal ****
                    elif client == clients[-1]:
                        return deal_cards(clients)
                               
                else:
                    break
 
    second_hand = secondRoundHand()
       
        
    client_hand_dict[trump_client] += second_hand[1] + [rand_trump]    
    trump_client.send(pickle.dumps({'hand 2': client_hand_dict[trump_client]}) + b'|')

    for j, k in zip([l for l in clients if l != client], second_hand[0]):
        client_hand_dict[j] += k
        # send the cards to each player
        j.send(pickle.dumps({'hand 2': client_hand_dict[j]}) + b'|')

    return tricks(clients, trump, trump_client, client_hand_dict)
    #return declInput(clients, trump, trump_client, client_hand_dict)

def strToCard(string_):
    parsed_str = re.split(',*\s', string_)
    return card(Rank=parsed_str[0], Suit=parsed_str[1])

def tricks(clients, trump, trump_client, client_hand_dict):
    
    global score
    
    all_data = b''
    
    # holds all cards played during the trick
    trick_cards = {}
    
    # first person to play a card in first round's trick is whoever picked the trump suit. Thereafter, the first person
    # to play a card is whoever won the previous trick
    for client in clients[clients.index(trump_client):] + clients[:clients.index(trump_client)]:
        client.send(pickle.dumps({'play_card': 1}) + b'|')
        
        while 1:
            data = client.recv(1024)
            all_data += data
            
            if data and b'|' in all_data:
                to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
                print(to_analyse)
                all_data = all_data[all_data.index(b'|') + 1:]
                card_played = strToCard(to_analyse)
                if card_played not in deck or card_played not in client_hand_dict[client]:
                    all_data = b''
                    client.send(pickle.dumps({'play_card': 2}) + b'|')
                else:
                    # if the player is the first one to play a card during a trick
                    if client == trump_client:
                        legal_card = card_played
                        trick_cards[client] = card_played
                        break
                    else:
                        # other players must play a card of the same suit as legal_card. If a player doesn't
                        # hold a card of that suit, he must play a trump suit card. If the player doesn't have a trump
                        # suit card, he can play any card in his hand.
                        if list(filter(lambda x: x.Suit == legal_card.Suit, client_hand_dict[client])):
                            print('We got the same stuff as the trump guy')
                            legal_hand = list(filter(lambda x: x.Suit == legal_card.Suit, client_hand_dict[client]))
                        elif list(filter(lambda x: x.Suit == trump, client_hand_dict[client])):
                            print('We have to use a trump card')
                            legal_hand = list(filter(lambda x: x.Suit == legal_card.Suit, client_hand_dict[client]))
                        else:
                            print('play whatever')
                            legal_hand = client_hand_dict[client]
                        
                        print('Your legal_hand is: ', legal_hand)
                        
                        # if the card is not allowed to be played, e.g. player has a card of same suit as legal_card but 
                        # plays a trump suit card, ask to input the card again
                        if card_played not in legal_hand:
                            all_data = b''
                            client.send(pickle.dumps({'play_card': 2}) + b'|')
                        else:
                            trick_cards[client] = card_played
                            break
                    
        client_hand_dict[client].pop(client_hand_dict[client].index(card_played))
                
    list_ = list(trick_cards.values())
    list_.sort(key=lambda x: (x.Suit == trump, card_vals['trump'][x.Rank] if x.Suit == trump else card_vals['standard']))
    
    print(*list(trick_cards.values()), sep='\n')
    
    for player_, card_ in trick_cards.items():
        if list_[-1] == card_:
            for team, player_list in teams.items():
                if player_ in player_list:
                    score[team] += sum([card_vals['trump'][i.Rank] if i == trump else card_vals['standard'][i.Rank] for i in list_])
    
    print(score)
    
    if len(list(filter(None, client_hand_dict.values()))):
        return tricks(clients, trump, trump_client, client_hand_dict)
    else:
        return None
    

def declInput(clients, trump, trump_client, client_hand_dict):
    """
    Ask player for any declarations and checks if declarations are valid
    """
    
    global score
    
    print('*******************', clients)
    
    # Sort both hands by suit and rank
    for client, hand in client_hand_dict.items():
        hand.sort(key=lambda x: (x[1], hierarchy_[x[0]]))
        
    # Empty byte string where all the incoming socket data will be dumped     
    all_data = b''
    
    # dictionary to store all player declarations. This is to be used when we have declarations from 2 or more
    # players and we need to decide which declaration is superior
    decl_dict = {}
    
    # prompt player to input any declarations
    for client, hand in client_hand_dict.items():
        client.sendall(pickle.dumps({'any_declarations': 1}) + b'|')
        
        while 1:
            data = client.recv(1024)
            all_data += data
            
            if data and b'|' in all_data:
                to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
                print(to_analyse)
                all_data = all_data[all_data.index(b'|') + 1:]
                
                # if player has nothing to declare move to the next iteration in the main for loop
                if to_analyse == '' or to_analyse == 'none':
                    decl_dict[client] = []
                    break
                
                declaration = []
                
                for i in re.split('\sand\s', to_analyse):
                    declaration += [[card(j, k) for j, k in zip(re.split(',*\s', i)[0::2], re.split(',*\s', i)[1::2])]]
                    
                print('declaration is {}'.format(declaration))
                
                CV = checkDeclValidity(to_analyse)
                DC = declarationChecks(declaration, hand, trump)
                
                if CV != 1 or DC != 1:
                    # if declaration hasn't passed the relevant checks, reset declarations and all_data variables
                    # and prompt user for input again
                    print('declaration checks results', DC)
                    declaration = []
                    all_data = b''
                    client.sendall(pickle.dumps({'any_declarations': 2}) + b'|')
                else:
                    decl_dict[client] = declaration
                    break
    
    # Check for Bela
    decl_dict = checkBela(decl_dict, trump)
    
    # Check if there are any declarations at all
    if checkAnyDecl(decl_dict): # if checkAnyDecl() returns 1
        max_decl_team = declMax(decl_dict, trump)
        
        print(f'max_decl_team is: {max_decl_team}')
        
        # if one team holds a declaration with the highest value, all of their declarations are counted towards the final score
        if max_decl_team: 
            decl_to_score = sum([decl_values[declToString(decl)] for decl in flatListFromDictVal(decl_dict, teams[max_decl_team])])
            print(f'{max_decl_team} holds the highest value declaration so all of their declarations count.\n {max_decl_team} receives {decl_to_score} points')
            
            score[max_decl_team] += sum([decl_values[declToString(decl)] for decl in flatListFromDictVal(decl_dict, teams[max_decl_team])])
    
    print(score)
    print('Done with declarations')


host = ''
port = 54321

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


print('socket created')

try:
    s.bind((host, port))
except socket.error:
    print('Binding failed')
    sys.exit()
    
print('Socket has been bound')

s.listen(5)
print('socket is ready')

clients = []
    
while 1:
    conn, addr = s.accept()
    clients.append(conn)

    # clients[conn] = id(conn)
    print('connected to client {} {}:{}'.format(id(conn), addr[0], addr[1]))
    
#     if conn:
#         threading.Thread(target=greeting, args=(conn,)).start()
    if len(clients) == 4:
        print('\n****starting session****\n')
        
        shuffle(clients) # shuffle players around
        dealer = choice(clients) # pick the player who will deal the cards
        
        teams = {'team_1': clients[::2], 'team_2': clients[1::2]} # create the two teams
        
        
            
        
        threading.Thread(target=dealCards, args=(clients,)).start()  
        
"""
stage 1. deal cards and pick trump suit. if all players pass deal cards again

"""