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
       
    first_hand = [[card(Rank='10', Suit='Hearts'), card(Rank='J', Suit='Hearts'), card(Rank='Q', Suit='Hearts')], [card(Rank='7', Suit='Clubs'), card(Rank='8', Suit='Clubs')]]
    
    client_hand_dict = {}
    
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
                    
                    #second_hand = secondRoundHand()
                    
                    print('sending hand 2')

                    secondee = [[card(Rank='10', Suit='Hearts'), card(Rank='J', Suit='Hearts')]]
                    second_hand = secondee, [card(Rank='Q', Suit='Hearts'), card(Rank='K', Suit='Hearts')]
                    
                    client_hand_dict[client] += second_hand[1] + [rand_trump]
                    print(client_hand_dict[client])
                    client.send(pickle.dumps(['hand 2', client_hand_dict[client]]) + b'|')
                    print('send hand 2')
                      
                    time.sleep(1.5)
                    
                    for j, k in zip([l for l in clients if l != client], second_hand[0]):
                        client_hand_dict[j] += k
                        # send the cards to each player
                        j.send(pickle.dumps(['hand 2', client_hand_dict[j]]) + b'|')
                    
                    return declInput(trump, trump_client, client_hand_dict)

                            
                    # return tricks(clients, trump, trump_client, client_hand_dict)
                    # return declInput(clients, trump, trump_client, client_hand_dict)
                else:
                    for i in [j for j in clients if j != client]:
                        i.sendall(pickle.dumps(['o_pass', players[client]]) + b'|')

                    time.sleep(1.5)
                    break

    
    # if all players pass on the random trump suit, free for all 
    if not trump:
        for client in clients:
            if client == clients[-1]:
                print('yes')
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
                    if pickle.loads(data) in suits:
                        trump = pickle.loads(data)
                        trump_client = client
                        for i in clients:
                            i.sendall(pickle.dumps(['trump', trump]) + b'|')

                        for i in [j for j in clients if j != client]:
                            i.sendall(pickle.dumps(['o_trump', players[client]]) + b'|') 
                            print('sent o_trump')  
                                  
                    
                    else:
                        for i in [j for j in clients if j != client]:
                            i.sendall(pickle.dumps(['o_pass', players[client]]) + b'|')

                        time.sleep(1.5)
                        break
 
    # second_hand = secondRoundHand()
       
        
    # client_hand_dict[trump_client] += second_hand[1] + [rand_trump]    
    # trump_client.send(pickle.dumps({'hand 2': client_hand_dict[trump_client]}) + b'|')

    # for j, k in zip([l for l in clients if l != client], second_hand[0]):
    #     client_hand_dict[j] += k
    #     # send the cards to each player
    #     j.send(pickle.dumps({'hand 2': client_hand_dict[j]}) + b'|')
    #return declInput(clients, trump, trump_client, client_hand_dict)

def declInput(trump, trump_client, client_hand_dict):
    """
    Ask player for any declarations and checks if declarations are valid
    """
        
    # # Sort both hands by suit and rank
    # for client, hand in client_hand_dict.items():
    #     hand.sort(key=lambda x: (x[1], hierarchy_[x[0]]))
        
    # Empty byte string where all the incoming socket data will be dumped     
    all_data = b''
    
    # dictionary to store all player declarations. This is to be used when we have declarations from 2 or more
    # players and we need to decide which declaration is superior
    decl_dict = {}
    
    # prompt player to input any declarations
    for client, hand in client_hand_dict.items():
        client.sendall(pickle.dumps({'any_decl': 1}) + b'|')

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