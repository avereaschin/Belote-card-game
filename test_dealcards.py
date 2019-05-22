import socket
import sys
import pickle
from card_vars import ranks, suits, card, deck, deck_dealing, decl_values, card_vals, hierarchy_
from random import choice, shuffle 
from itertools import chain
import threading
import time
import re

class Score():
    """
    Keeps track of player scores
    """
    score_dict = {'player 1': 0, 'player 2': 0, 'player 3': 0, 'player 4': 0}

    def add_(self, player, points):
        self.score_dict[player] = points
        
    def clear_(self):
        for key in list(self.score_dict.keys()):
            score_dict[key] = 0

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
    3. Do any cards in appear in multiple declarations?

    If the answer to any of the above questions is NO then the function will return None.
    """
    
    # Check 1
    # print(declarations)
    # if declarations == [] or declarations == ['none']:
    #     return 1
    
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
    This function scans players' declarations for Bela. If one is found this function removes the Bela from the decl_dict before
    it feeds into the declComp() function. It also calls the Score.add_ function which gives the player who holds Bela 20 points.
    """
    
    bela = [card(Rank='Q', Suit=trump), card(Rank='K', Suit=trump)]

    for client, decl in decl_dict.items():        
       
        if bela in decl:
            # Add 20 points to the player holding Bela
            score.add_(players[client], 20)
            for i in clients:
                if i == client:
                    i.sendall(pickle.dumps(['score', ('you', 20)]) + b'|') 
                else:
                    i.sendall(pickle.dumps(['score', (players[client], 20)]) + b'|') 
            
            print(f'{players[client]} has declared Bela and gets +20 points!')
        
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
    Takes a declaration dict and flattens its values into one list. Useful when dicts have nested lists as values. Also filters out any empty lists.
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

def firstRoundHand():
    """
    First round hand. Players are dealt 5 cards each
    """
    return [[choicePop() for i in range(5)] for i in range(4)]

def secondRoundHand():
    """
    Second round hand. After trump suit is chosen, players are dealt 3 cards each (one player gets 2 cards + trump card)
    """
    return [[choicePop() for j in range(3)] if i != 0 else [choicePop() for j in range(2)] for i in range(4)]
    
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
    
    flat_ = flatListFromDictVal(decl_dict, list(decl_dict.keys()))
    matrix_ = flatListMatrix(flat_, trump)
    
    max_ = max(matrix_)
    
    if matrix_.count(max_) > 1:
        return 0
    else:
        max_decl = flat_[matrix_.index(max_)]

        for client, declaration in decl_dict.items():
            if max_decl in declaration:
                return client, max_decl        

def declMsg(decls):
    """
    Compiles a message regarding a player's declaration(s) to be sent to his opponents. Declarations aren't supposed to reveal a player's
    cards until we know for sure that the player holds the highest declaration. As a result, if a player declares a 3 card sequnce: [J Hearts,
    Q Hearts, K Hearts], his opponents will only be told that "a 3 card sequence (high K)" has been declared.
    """
    msg = ''

    for i, decl in enumerate(decls):
        print(decl)
        if i > 0:
            msg += ' ' + 'and'
            print(msg)
        if declType(decl) == 1:
            msg += f'a {declLen(decl)} card sequence (high {decl[-1].Rank})' 
            print(msg)           
        elif declType(decl) == 2:
            msg += 'a square'
            print(msg)
        else:
            msg += 'Bela'
            print(msg)

    return msg

def dealCards(clients):
    
    """
    Messages are separated by b'|'
    """
    all_data = b''    
    
    # stage 1. deal cards and pick trump suit 
    trump = ''
    
    # rand_trump = choice(deck_dealing)
    rand_trump = card(Rank='10', Suit='Hearts')
    print(f'rand_trump is {rand_trump}')

    # remove trump card from deck before dealing cards
    deck_dealing.pop(deck_dealing.index(rand_trump))
    
    # holds players as dict key and their cards as dict value       
    client_hand_dict = {}

    # first_hand = firstRoundHand()
    first_hand = [[card(Rank='J', Suit='Hearts'), card(Rank='Q', Suit='Hearts'), card(Rank='K', Suit='Hearts'), card(Rank='A', Suit='Hearts')],
                 [card(Rank='J', Suit='Clubs'), card(Rank='Q', Suit='Clubs'), card(Rank='K', Suit='Clubs'), card(Rank='A', Suit='Clubs')]]

    for client in clients:
        client.send(pickle.dumps(['clients', [f'player {i}' if j != client else 'you' for i, j in enumerate(clients, 1)]]) + b'|')

    for client, hand in zip(clients, first_hand):
        client_hand_dict[client] = hand
        client.sendall(pickle.dumps(['hand 1', hand]) + b'|')
        print('sent hand to ', players[client])
        client.sendall(pickle.dumps(['rand_trump', rand_trump]) + b'|')
        print('sent rand_trump')       
    
    # players chose whether to play randomly chosen trump suit                   
    for client in clients:
        client.sendall(pickle.dumps(['round_1', True]) + b'|')
        print(f'client {client}\'s turn to pick trump')
        for i in [j for j in clients if j != client]:
            i.send(pickle.dumps(['o_think', players[client]]) + b'|')

        print('sent round_1 to ', players[client])
        
        while 1:
            data = client.recv(1024)
            all_data += data
            
            if data and b'|' in all_data:
                to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
                print(to_analyse)
                all_data = all_data[all_data.index(b'|') + 1:]
                
                if to_analyse == 'play':
                    trump = rand_trump[1]
                    trump_client = client 
                    print(f'{client} picked trump suite: {trump}')
                    for i in clients:
                        # i.sendall(pickle.dumps(f'client {client} has picked trump suit {trump}') + b'|')
                        i.sendall(pickle.dumps(['trump', trump]) + b'|')
                    
                    for i in [j for j in clients if j != client]:
                        i.sendall(pickle.dumps(['o_trump', players[client]]) + b'|') 
                        print('sent o_trump') 

                    # if trump suit is picked deal the second round of cards (3 cards to each player)
                    
                    # second_hand = secondRoundHand()
                    second_hand = [[], []]
                    
                    time.sleep(1)

                    client_hand_dict[client] += second_hand[0] + [rand_trump]
                    client.send(pickle.dumps(['hand 2', client_hand_dict[client]]) + b'|')
                              
                    for j, k in zip([l for l in clients if l != client], second_hand[1:]):
                        client_hand_dict[j] += k
                        j.send(pickle.dumps(['hand 2', client_hand_dict[j]]) + b'|')
                    
                    # send instruction to client to start sending declarations
                    for i in clients:
                        i.sendall(pickle.dumps(['declaration', True]) + b'|')
                    
                    time.sleep(1.5)        

                    # return tricks(clients, trump, trump_client, client_hand_dict)
                    return declInput(trump, trump_client, client_hand_dict)
                else:
                    for i in [j for j in clients if j != client]:
                        i.sendall(pickle.dumps(['o_pass', players[client]]) + b'|')

                    time.sleep(1.5)
                    break

    
    # if all players pass on the random trump suit, free for all 
    if not trump:
        for client in clients:
            if client == clients[-1]:
                client.send(pickle.dumps(['round_2_must_pick', True]) + b'|')
            else:
                client.send(pickle.dumps(['round_2', True]) + b'|')
            
            for i in [j for j in clients if j != client]:
                i.send(pickle.dumps(['o_think', players[client]]) + b'|')

            print('sent round_2 to ', players[client])
            
            while 1:
                data = client.recv(1024)
                all_data += data
            
                if data and b'|' in all_data:
                    to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
                    print(to_analyse)
                    all_data = all_data[all_data.index(b'|') + 1:]
                    # if picked a valid suit deal rest of the cards and call declInput()
                    if pickle.loads(data) in suits:
                        trump = pickle.loads(data)
                        trump_client = client
                        for i in clients:
                            i.sendall(pickle.dumps(['trump', trump]) + b'|')

                        for i in [j for j in clients if j != client]:
                            i.sendall(pickle.dumps(['o_trump', players[client]]) + b'|') 
                            print('sent o_trump')  
                                  
                        second_hand = secondRoundHand()
                        
                        time.sleep(1)

                        client_hand_dict[client] += second_hand[0] + [rand_trump]
                        client.send(pickle.dumps(['hand 2', client_hand_dict[client]]) + b'|')
                                                  
                        for j, k in zip([l for l in clients if l != client], second_hand[1:]):
                            client_hand_dict[j] += k
                            # send the cards to each player
                            j.send(pickle.dumps(['hand 2', client_hand_dict[j]]) + b'|')

                        # send instruction to client to start sending declarations
                        for i in clients:
                            i.sendall(pickle.dumps(['declaration', True]) + b'|')

                        time.sleep(1.5)

                        return declInput(trump, trump_client, client_hand_dict)
                    
                    else:
                        for i in [j for j in clients if j != client]:
                            i.sendall(pickle.dumps(['o_pass', players[client]]) + b'|')

                        time.sleep(1.5)
                        break


def declInput(trump, trump_client, client_hand_dict):
    """
    Ask player for any declarations and checks if declarations are valid
    """

    # Empty byte string where all the incoming socket data will be dumped     
    all_data = b''
    
    # dictionary to store all player declarations. This is to be used when we have declarations from 2 or more
    # players and we need to decide which declaration is superior
    decl_dict = {}
    
    # prompt player to input any declarations
    for client in clients[clients.index(trump_client):] + clients[:clients.index(trump_client)]:
    # for client, hand in client_hand_dict.items():

        client.sendall(pickle.dumps(['any_decl', True]) + b'|')

        for i in [j for j in clients if j != client]:
            i.send(pickle.dumps(['o_think', players[client]]) + b'|')
        
        while 1:
            data = client.recv(1024)
            all_data += data
            
            if data and b'|' in all_data:
                to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
                print(to_analyse)
                all_data = all_data[all_data.index(b'|') + 1:]
                
                # if player has nothing to declare move to the next iteration in the main for loop
                if to_analyse == 'none':
                    decl_dict[client] = []
                    for i in [j for j in clients if j != client]:
                        i.sendall(pickle.dumps(['o_no_decl', players[client]]) + b'|')
                        time.sleep(2)
                    break
                    
                print('declaration is {}'.format(to_analyse))
                
                DC = declarationChecks(to_analyse, client_hand_dict[client], trump)
                
                if DC != 1:
                    # if declaration hasn't passed the relevant checks, reset declarations and all_data variables
                    # and prompt user for input again
                    print('declaration checks results', DC)
                    declaration = []
                    all_data = b''
                    client.sendall(pickle.dumps(['any_decl_err', True]) + b'|')
                    client.sendall(pickle.dumps(['any_decl', True]) + b'|')
                else:
                    decl_dict[client] = to_analyse
                    
                    for i in [j for j in clients if j != client]:
                        i.sendall(pickle.dumps(['o_decl', (players[client], declMsg(to_analyse))]) + b'|')
                        time.sleep(3)
                    break
    
    # Check for Bela
    decl_dict = checkBela(decl_dict, trump)
    
    # Check if there are any declarations at all
    if checkAnyDecl(decl_dict): # if checkAnyDecl() returns 1
        max_decl = declMax(decl_dict, trump)
        
        print(f'max_decl is: {max_decl}')
        
        # if one team holds a declaration with the highest value, all of their declarations are counted towards the final score
        if max_decl: 
            decl_to_score = sum([decl_values[declToString(decl)] for decl in decl_dict[max_decl[0]]])
            print(f'{max_decl[0]} holds the highest value declaration so all of their declarations count.\n {max_decl[0]} receives {decl_to_score} points')
            score.add_(players[max_decl[0]], decl_to_score) 

            for i in clients:
                if i == max_decl[0]:
                    i.sendall(pickle.dumps(['max_decl', ('you', max_decl[1])]) + b'|')
                else:
                    i.sendall(pickle.dumps(['max_decl', (players[max_decl[0]], max_decl[1])]) + b'|')
                i.sendall(pickle.dumps(['score', (players[client], decl_to_score)]) + b'|')
        else:
            for i in clients:
                i.sendall(pickle.dumps(['decl_tie', True]) + b'|')
    
    print(score)
    print('Done with declarations')


score = Score()

host = ''
port = 54321

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('socket created')

try:
    s.bind((host, port))
except socket.error:
    sys.exit()
    
print('Socket has been bound')

s.listen(5)
print('socket is ready')


# def main():
    
clients = []
score = Score()    

while 1:
    conn, addr = s.accept()
    clients.append(conn)

    # clients[conn] = id(conn)
    print('connected to client {} {}:{}'.format(id(conn), addr[0], addr[1]))
    
    if len(clients) > 1:
        print('\n****starting session****\n')
        
        shuffle(clients) # shuffle players around
        dealer = clients[0] # pick the player who will deal the cards

        players = {j: f'player {i}' for i, j in enumerate(clients, 1)}
        
        dealCards(clients) 

# if __name__ == '__main__':
#     main()