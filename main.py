import os
import textplayer.textPlayer as tp
import discord
import asyncio
import glob
import sys

client = discord.Client()

sessions = {}

@client.event
@asyncio.coroutine
def on_message(message):
    if message.channel.name != 'infocom':
        return

    if message.content.startswith('!play'):
        parts = message.content.split(' ')
        if len(parts) >= 2:
            t = tp.TextPlayer(parts[1])
            if message.channel.id in sessions:
                try:
                    sessions[message.channel.id].quit()
                except:
                    sessions.pop(message.channel.id, None)
            start_info = t.run()

            if not t.game_loaded_properly:
                yield from client.send_message(message.channel, "game failed to start")
                return

            sessions[message.channel.id] = t
            yield from client.send_message(message.channel, start_info)
        else:
            games = [os.path.basename(x) for x in glob.glob('./textplayer/games/*.z*')]
            games.sort()
            yield from client.send_message(message.channel, "need a game name: " + ', '.join(games))

    if message.content.startswith('.'):
        if not message.channel.id in sessions:
            yield from client.send_message(message.channel, "no game started, start one with !play (name)")
            return
 
        try:
            t = sessions[message.channel.id]
            command_output = t.execute_command(message.content[1:])
        except:
            e = sys.exc_info()[0]
            yield from client.send_message(message.channel, "resetting frotz due to exception: %s" % e)
            sessions.pop(message.channel.id, None)
            return
        #score = t.get_score()
        #if score is None:
        #    score = ('???', '???')
        #outmsg = "**Score**: %s/%s\n\n%s" % (score[0], score[1], command_output)
        if len(command_output) == 0:
            command_output = "Received empty response from interpreter"
        yield from client.send_message(message.channel, command_output)

client.run(sys.argv[1])
