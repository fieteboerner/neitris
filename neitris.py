#! /usr/bin/python
#
#    Neitris - A multiplayer Tetris clone 
#    Copyright (C) 2006 Alexandros Kostopoulos (akostopou@gmail.com)
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
import thread
from neitris_cfg import *
from neitris_theme_loader import ThemeLoader
import neitris_class
import neitris_utils
import copy
from neitris_data import powerups
import neitris_cli
from Queue import *
import struct
import zlib
from socket import socket, AF_INET, SOCK_STREAM
import time
import pygame, sys, os, pickle
from pygame.locals import *

PORT = 7777

rqueue = Queue()
wqueue = Queue()

State = "Idle"

pygame.init()
window = None
screen = None
background = None
DONE=0

theme = ThemeLoader(THEME)
bricks = theme.get_bricks()

dotTheme = ThemeLoader('dot')
dots = dotTheme.get_bricks()

#matrix = neitris_class.Matrix(0,0)

#matrix_enemy = neitris_class.Matrix(0,0)

players = {}

clock = pygame.time.Clock()
pygame.key.set_repeat(300, 50)

STARTGAME_EVENT = USEREVENT + 1
TICKEVENT = USEREVENT + 2

delay = 0

tick = 0

pygame.time.set_timer(pygame.USEREVENT, 10)

speed = [9, 13, 15, 20, 25, 30, 40, 50, 70, 100]
if MAXLEVEL:
    speed = map(lambda x: max([x, speed[10-MAXLEVEL]]), speed)

count = 0
lines = 0

sent_bytes = 0
sent_times = 0
sent_min = 0
sent_max = 0

state_change = 0
send_last_update = 0

playerid = 0

donatorlines = 0


def EndGame():
    global State
    global sent_bytes, sent_times, sent_min, sent_max
    global playerid
    global wqueue
    global send_last_update

    State = "Idle"
    print "GAME IS OVER!!!!"
    print "sent %d bytes,%d times, %d bytes/time avg\n" % \
          (sent_bytes, sent_times, sent_bytes / sent_times)

    print "sent_min: %d, sent_max: %d\n" % (sent_min, sent_max)

    msg = neitris_utils.MsgPack(neitris_utils.GAMEOVER, "", 0, playerid)
    wqueue.put_nowait(msg)
    send_last_update = 1


def input(events, matrix):
    global State
    global speed, count, lines
    global donatorlines
    global state_change
    global sent_bytes;
    global sent_times, sent_min, sent_max;
    global playerid
    global wqueue, rqueue
    global delay
    global tick
    global speed
    global TICKEVENT

    curlines = 0

    for event in events:
        if event.type == QUIT or (event.type == KEYDOWN and event.key == KEY_QUIT):
            sys.exit(0)
        elif  event.type == KEYDOWN and event.key == KEY_START \
                 and State == "Idle":
            State = "WaitStart";
            msg = neitris_utils.MsgPack(neitris_utils.STARTREQ, "", 0, playerid)
            print "msg to send: ", msg[5:], " with len: ", len(msg)
            wqueue.put_nowait(msg)
        elif  event.type == KEYDOWN and event.key == KEY_RSTWINS:
            if players[playerid] != None:
                players[playerid].victories = 0
        elif State == "WaitStart" and event.type == STARTGAME_EVENT:

            pygame.time.set_timer(TICKEVENT, 100)
            matrix.Initialize()
            matrix.NewShape()
            State = "Playing"
            count = 0
            lines = 0

            state_change = 1

            sent_bytes = 0
            sent_times = 0
            sent_min = 1000
            sent_max = 0

            #players[playerid].victim = -1
            #for p in players:
            #    if p != playerid:
            ###        players[playerid].victim = p
            #      break
            players[playerid].ChangeVictim("init")
            print "Initial Victim is player nr ", players[playerid].victim


            print "Game is starting"

        elif State == "Playing":

            if ( (event.type == USEREVENT and \
                  count >= speed[players[playerid].speedidx] ) or
                (event.type == KEYDOWN and event.key == KEY_DOWN)):

                count = 0
                state_change = 1

                if matrix.MoveDown()==0:
                    curlines = curlines + matrix.ClearCompleted()

                    #print "cleared lines: ", lines

                    if(matrix.NewShape()==0):
                        EndGame()
                        pygame.time.set_timer(TICKEVENT, 0)

            if (event.type == USEREVENT and \
                count < speed[players[playerid].speedidx]):
                count = count + 1

            if event.type == USEREVENT:
                if delay == UPDATE_FREQ:
                    delay = 0
                else:
                    delay = delay + 1

            if event.type == TICKEVENT:
                tick = 1

            if event.type == KEYDOWN:
                if event.key == KEY_LEFT:
                    matrix.MoveLeft()
                elif event.key == KEY_RIGHT:
                    matrix.MoveRight()
                elif event.key == KEY_RLEFT:
                    matrix.RotateLeft()
                elif event.key == KEY_RRIGHT:
                    matrix.RotateRight()
                elif event.key == KEY_DROP:
                    matrix.Drop()
                    curlines = curlines + matrix.ClearCompleted()
                    #print "cleared lines: ", lines

                    if(matrix.NewShape()==0):
                        EndGame()
                elif event.key == KEY_USEANTIDOTE:
                    players[playerid].UseAntidote()
                elif event.key == KEY_VICTIM:
                    players[playerid].ChangeVictim("normal")

                state_change = 1


    lines = lines + curlines
    donatorlines = donatorlines + curlines
    return



def ProcessMsg(rqueue):
    global state_change
    global matrix_enemy
    global players
    global State
    global wqueue
    global screen, background

    while not rqueue.empty():

        msg = rqueue.get_nowait()
        (length, data, cmd, dst, src) = neitris_utils.MsgUnpack(msg)

        #print "received msg ", msg, " with data: ",data, " and cmd: ",cmd
        if cmd == neitris_utils.SENDSTATE:

            #data = zlib.decompress(data)

            state_change = 1
            players[src].PutMatrixStream(data)

        elif cmd == neitris_utils.GAMEINFO:
            print "Got GAMEINFO msg:", data
            (pnr,) = struct.unpack("B", data[0])
            print "There are ", pnr," players in the game"
            window = None
            screen = None
            #background = None
            window = pygame.display.set_mode((theme.get_window_width() * pnr, theme.get_window_height()))
            pygame.display.set_caption('Neitris')

            screen = pygame.display.get_surface()

            data = data[1:]
            if players[playerid] == None:
                victories = 0
            else:
                victories = players[playerid].victories

            players={}
            for i in range(pnr):
                (pid, length) = struct.unpack("!BH",data[:3])
                playermatrix = neitris_class.Matrix(i * theme.get_window_width(), 0)
                playermatrix.pid = pid
                playermatrix.name = data[3:(length+3)]
                playermatrix.active = 1
                players[pid] = playermatrix
                #players.append([id, data[3:(length+3)]])
                data = data[(length+3):]

            print "The following players are in the game: "
            players[playerid].player_list = []
            players[playerid].player_dict_active = {}

            players[playerid].player_list.append(-1)
            players[playerid].player_dict_active[-1] = 1
            for i in players:
                print i, players[i].name
                players[playerid].player_list.append(i)
                if i != playerid:
                    players[playerid].player_dict_active[i] = 1
                else:
                    players[playerid].player_dict_active[i] = 0


            #simply store the entire playrs dict into the player obj
            for i in players:
                players[i].players = players
                players[i].victories = 0

            players[playerid].victories = victories

        elif cmd == neitris_utils.GAMESTART:
            data, = struct.unpack("B", data)
            if data > 0:
                font = pygame.font.Font(None, int(25 * SCALE_FACTOR))

                text = font.render("%i" % data, 1, theme.textColor, theme.bgColor)
                textpos = text.get_rect()
                textsurf = pygame.Surface(screen.get_size())
                textsurf.fill(theme.bgColor)
                textpos.centerx = textsurf.get_rect().centerx
                textpos.centery = 270

                textsurf.blit(text, textpos)
                screen.blit(textsurf, (0, 0))
                pygame.display.update()
                print "Counting: ", data
            else:
                print "GO!!!"
                startgame = pygame.event.Event(STARTGAME_EVENT, start=0)
                pygame.event.post(startgame)
        elif cmd == neitris_utils.GAMEOVER:
            if src == 0:
                print "Game is over!!!"
                State = "Idle"
            else:
                print "Player %s has lost..." % (players[src].name)
                players[src].active = 0

                players[playerid].player_dict_active[src] = 0
                if players[playerid].victim == src:
                    players[playerid].ChangeVictim("victimdied")

        elif cmd == neitris_utils.INCRVICTS:
            print "You are the winner of this game"
            players[playerid].victories = players[playerid].victories + 1
            print "Victories: ", players[playerid].victories

            # Send last update to other players
            data = players[playerid].GetMatrixStream()
            msg = neitris_utils.MsgPack(neitris_utils.SENDSTATE, data, 0,
                                       playerid)
            wqueue.put_nowait(msg)

            players[playerid].DrawMatrix(screen, bricks, dots, players,
                                         background)
            pygame.display.flip()
        elif cmd == neitris_utils.INCRSPEED:
            if players[playerid].speedidx != 0:
                players[playerid].speedidx = players[playerid].speedidx - 1
            print "Increasing speed. New speed: ", \
                  speed[players[playerid].speedidx]

        elif cmd == neitris_utils.POWERUP:
            pup_id, = struct.unpack("B", data[0])
            pupobj = copy.deepcopy(powerups[pup_id])
            if pupobj.pid == 255: # DONATORRCVD
                linesrcvd, = struct.unpack("B", data[1])
                print "From player", src, "got donator and ", linesrcvd,"lines"
                pupobj.lines = linesrcvd
            elif pupobj.pid == 17: # SWAPSCR
                dir, =  struct.unpack("B", data[1])
                data = data[2:]
                if dir == 0: # just rcvd swapscreen
                    # If not dead, send screen to peer
                    if State == "Playing" :
                        dataout = players[playerid].GetSwapData()
                        dataout = struct.pack("BB", 17, 1) + dataout

                        msg = neitris_utils.MsgPack(
                            neitris_utils.POWERUP, dataout,
                            src, playerid)
                        wqueue.put_nowait(msg)
                        players[playerid].PutSwapData(data)
                else: # received back others data
                    players[playerid].PutSwapData(data)



            else:
                print "From player ", src, " got ", pupobj.name, " with id ", pupobj.pid

            players[playerid].powerups_active[pup_id]=pupobj

def neitris_main_loop(rq, wq):
    global state_change, playerid
    global sent_times, sent_bytes, sent_max, sent_min

    global screen, background, window
    global State

    global wqueue, rqueue
    global players

    global delay
    global tick

    global donatorlines
    global send_last_update

    wqueue = wq
    rqueue = rq


    flash_powerup = 0

    # Initially, get user's name and sent it to server to register player
    playername=raw_input("enter a player name: ")
    msg = neitris_utils.MsgPack(neitris_utils.REGPLAYER, playername, 0, 0)
    print "msg to send: ", msg[5:], " with len: ", len(msg)
    wqueue.put_nowait(msg)

    wait_id = 0

    # Then wait for registration acknowledgement
    while not wait_id:
        while not rqueue.empty():
            msg = rqueue.get_nowait()
            (length, data, cmd, dst, src) = neitris_utils.MsgUnpack(msg)
            if cmd == neitris_utils.REGPLAYERACK:
               (playerid,) = struct.unpack("B", data)
               wait_id = 1
               break
            elif cmd == neitris_utils.REGPLAYERNACK:
               print "Cannot Join!"
               print "Reason given from server:",data
               readsock.close()
               sys.exit(0)

    print "Registered with the Server, got id: ", playerid
    players[playerid] = None



    window = pygame.display.set_mode((theme.get_window_width(), theme.get_window_height()))
    pygame.display.set_caption('Neitris')

    screen = pygame.display.get_surface()
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(theme.bgColor)

    font = pygame.font.Font(None, int(25 * SCALE_FACTOR))

    text = font.render("Press START to start game", 1, theme.textColor, theme.bgColor)
    textpos = text.get_rect()
    textsurf = pygame.Surface(screen.get_size())
    textsurf.fill(theme.bgColor)
    textpos.centerx = textsurf.get_rect().centerx
    textpos.centery = 270

    textsurf.blit(text, textpos)
    screen.blit(textsurf, (0, 0))
    pygame.display.flip()

    while True:
        # Process Messages from the server and other clients
        ProcessMsg(rqueue)

        # Process events
        input(pygame.event.get(), players[playerid])


        # periodically (10 times/sec) send updates to other clients
        if (delay == UPDATE_FREQ and State == "Playing") or \
              send_last_update == 1:

            delay = 0
            send_last_update = 0
            data = players[playerid].GetMatrixStream()

            #data = zlib.compress(data,9)
            l = len(data)
            sent_bytes = sent_bytes  + l

            sent_times = sent_times + 1

            if l > sent_max:
                sent_max = l
            if l < sent_min:
                sent_min = l

            msg = neitris_utils.MsgPack(neitris_utils.SENDSTATE, data, 0,
                                       playerid)
            wqueue.put_nowait(msg)

            if not send_last_update:
                flash_powerup = players[playerid].MonitorPowerups()


                # Generate and destroy powerups in the matrix
                if GENERATE_POWERUPS:
                    players[playerid].GeneratePowerup()


        # Process Cleared (i.e. from the matrix) Powerups
        if State == "Playing":
            players[playerid].ProcessClearedPowerups(wqueue)
            players[playerid].ProcessActivePowerups(donatorlines, wqueue)
            donatorlines = 0

            if tick:
                tick = 0
                players[playerid].ProcessActivePowerupsTimed()



        # Update Screen
        if state_change or flash_powerup:

            for p in players:
                #screen.blit(background, (players[p].srcx, 0))
                players[p].DrawMatrix(screen, bricks, dots, players,
                                      background)
            pygame.display.flip()
            state_change = 0
            flash_powerup = 0



        pygame.time.wait(10)




def neitris_main():
    while 1:
        neitris_main_loop(rqueue, wqueue)


def StartClient():
    # Start two threads, one reading, one writing
    thread.start_new(neitris_cli.ChatRead, (7777, rqueue, readsock))
    thread.start_new(neitris_cli.ChatWrite, (7778, wqueue, readsock))
    time.sleep(0.5) # should remove this, not needed
    neitris_main()

    return

if __name__=="__main__":
    global readsock
    global HOSTNAME

    print "Neitris Version 0.1beta, $Revision: 34 $"
    print "   Copyright (C) 2006 Alexandros Kostopoulos"
    print "\nNeitris comes with ABSOLUTELY NO WARRANTY. This is free software,"
    print "and you are welcome to redistribute it under certain conditions; "
    print "See the GNU General Public License for more details.\n\n"

    if len(sys.argv)==1:
        print "Enter server's IP: "
        HOSTNAME = raw_input()
        if HOSTNAME == "":
            HOSTNAME = "127.0.0.1"

        print HOSTNAME
    else:
        HOSTNAME = sys.argv[1]

    readsock = socket(AF_INET, SOCK_STREAM)
    readsock.connect((HOSTNAME, PORT))
#    readsock.send("<READ>")
    connected = 1

    StartClient()
