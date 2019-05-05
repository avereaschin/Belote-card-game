# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 18:01:05 2018

@author: Andrei
"""

import socket
import sys
import pickle
from card_vars import ranks, suits, card
from random import choice 
import threading
import re
import queue
import select
import time

q = queue.Queue()

    
def receiving():

    host = 'localhost'
    port = 54321

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    try:
        s.connect((host, port))
    except socket.error:
        print('couldn\'t connect')
        sys.exit()
        

    # server messages to be placed in a queue for processing    

    trump = ''
    all_data = b''
    
    while 1:

        time.sleep(1)
        
        readable, _, _ = select.select([s], [], [])
        
        # check if there is any information to be read from the socket
        # if yes, start receiving data
        if len(readable) != 0:
            data = s.recv(1024)    
            # all data received is dumped into all_data variable
            # all_data is then processed in the loop below where we look
            # for any message separators b'|'. All messages are popped out
            # of all_data  for processing and any leftover parts that were 
            # concatenated into the TCP packet and are missing a message  
            # separator are left in all_data unitl the next message separator 
            # is received
            all_data += data
                           
                
            if b'|' in all_data:
                to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
                # dump all messages into a queue
                all_data = all_data[all_data.index(b'|') + 1:]

                q.put(to_analyse)
                print('sent message to gamepy')


                # try:
                #     next_msg = msg_q.get_nowait()
                #     print('got message: ', next_msg)
                #     q.put(next_msg, False)
                # except queue.Empty:
                #     pass
                        
                    #     if isinstance(next_msg, dict):
                    #         try:
                    #             if next_msg['hand 1']:
                    #                 hand = next_msg['hand 1']
                    #                 print(f'your hand is:\n{hand}')
                    #                 continue
                    #         except KeyError:
                    #             pass

                    #         try:
                    #             if next_msg['hand 2']:
                    #                 hand += hand_msg['hand 2']
                    #                 print(f'your hand is:\n{hand}')
                    #                 continue
                    #         except KeyError:
                    #             pass
                            
                    #         try:
                                
                    #             if next_msg['rand_trump']:
                    #                 rand_trump = next_msg['rand_trump']
                    #                 print(f'randomly chosen trump suit is {rand_trump}')
                    #                 continue
                    #         except KeyError:
                    #             pass
                                
                    #         try:
                                
                    #             if next_msg['pick_trump'] == 1:
                    #                 sending(f'Would you like to play {rand_trump}?')
                    #                 continue
                    #         except KeyError:
                    #             pass
                               
                    #         try:
                    #             if next_msg['pick_trump'] == 2:
                    #                 sending(f'FFA Which suit would you like to play?')
                    #                 continue
                    #         except KeyError:
                    #             pass
                            
                    #         try:
                    #             if next_msg['trump']:
                    #                 trump = next_msg['trump']
                    #                 print(f'trump suit is {trump}')    
                    #         except KeyError:
                    #             pass
                            
                    # except queue.Empty:
                    #     print('Queue empty')
                         

                # else:
                #     print('Found trump. Breaking out of this loop into the next')
                #     break

                
            # print('Listening for declarations')
            # while 1:
            #     if b'|' in all_data:
            #         to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
            #         message_queue.put(to_analyse)
            #         all_data = all_data[all_data.index(b'|') + 1:]
                     
            #         try:
            #             next_msg = message_queue.get_nowait()
            #             print(next_msg)    
             
            #             if isinstance(next_msg, dict):
            #                 try:
            #                     if next_msg['any_declarations'] == 1:
            #                         sending('Any declarations?')
            #                     elif next_msg['any_declarations'] == 2:
            #                         sending('Invalid declaration. Try again')
            #                     elif next_msg['hand']:
            #                         print('\n', 'Dealt 3 extra cards. Your hand is now:\n', next_msg['hand'])
            #                 except KeyError:
            #                     pass
            #         except queue.Empty:
            #              print('Queue empty')
                
            #     else:
            #         break

            # print('Listening for tricks')
            # while 1:
            #     if b'|' in all_data:
            #         to_analyse = pickle.loads(all_data[:all_data.index(b'|')])
            #         message_queue.put(to_analyse)
            #         all_data = all_data[all_data.index(b'|') + 1:]
                     
            #         try:
            #             next_msg = message_queue.get_nowait()
            #             print(next_msg)    
             
            #             if isinstance(next_msg, dict):
            #                 try:
            #                     if next_msg['play_card'] == 1:
            #                         sending('Play a card')
            #                     elif next_msg['play_card'] == 2:
            #                         sending('Invalid card. Try again')
            #                 except KeyError:
            #                     pass
            #         except queue.Empty:
            #              print('Queue empty')
                
            #     else:
            #         break
                                 
                            

def sending(msg):
    print('i\'m here')
    message = input(msg)
    s.send(pickle.dumps(message) + b'|')
    return None

    
def main():
    threading.Thread(target=receiving).start()