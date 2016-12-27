import os
import textplayer.textPlayer as tp
import discord
import asyncio
import glob
import sys

reactions = {
    '\U00002B06': 'north',
    '\U00002B07': 'south',
    '\U00002B05': 'west',
    '\U000027A1': 'east',
    '\U0001F45D': 'inventory',
}

client = discord.Client()

sessions = {}

@asyncio.coroutine
def send_text_with_reactions(channel, text):
    msg = yield from client.send_message(channel, text)
    for r in reactions:
        yield from client.add_reaction(msg, r)

@asyncio.coroutine
def send_command(channel, command):
    try:
        t = sessions[channel.id]
        command_output = t.execute_command(command)
    except:
        e = sys.exc_info()[0]
        yield from client.send_message(channel, "resetting frotz due to exception: %s" % e)
        sessions.pop(channel.id, None)
        return

    if len(command_output) == 0:
        yield from client.send_message(channel, "Received empty response from interpreter")
        return

    yield from send_text_with_reactions(channel, command_output)

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
            yield from send_text_with_reactions(message.channel, start_info)
        else:
            games = [os.path.basename(x) for x in glob.glob('./textplayer/games/*.z*')]
            games.sort()
            yield from client.send_message(message.channel, "need a game name: " + ', '.join(games))

    if message.content.startswith('.'):
        if not message.channel.id in sessions:
            yield from client.send_message(message.channel, "no game started, start one with !play (name)")
            return
 
        yield from send_command(message.channel, message.content[1:])

@client.event
@asyncio.coroutine
def on_reaction_add(reaction, user):
    if user == client.user:
        return

    message = reaction.message
    if message.channel.name != 'infocom':
        return

    if not message.channel.id in sessions:
        return

    if not reaction.emoji in reactions:
        return

    yield from send_command(message.channel, reactions[reaction.emoji]) 

client.run(sys.argv[1])
