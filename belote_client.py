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
clnt_q = queue.Queue()

    
def testFunc(text):
    try:
        print('SERVER: ', pickle.loads(text[:text.index(b'|')]))
        q.put(pickle.loads(text[:text.index(b'|')]))
        return testFunc(text[text.index(b'|') + 1:])
    except ValueError:
        return text

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

        readable, _, _ = select.select([s], [], [], 0)
        
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
                       
                all_data = testFunc(all_data)

                # to_analyse = pickle.loads(all_data[:all_data.index(b'|')]) # problem two messages received at once so only one '|' gets decoded
                # # dump all messages into a queue
                # print('SERVER: ', to_analyse)
                
                # q.put(to_analyse)
                # # reset all_data but retain any incomplete messages (not found '|' message separator) 
                # all_data = all_data[all_data.index(b'|') + 1:]
                
        try:
            next_msg = clnt_q.get(False)
            print('CLIENT: ', next_msg)
            sending(s, next_msg)
        except queue.Empty:
            pass
                 

def sending(server, msg):
    server.send(pickle.dumps(msg) + b'|')
    print('sent msg: ', msg)

    
def main():
    threading.Thread(target=receiving).start()