#!./.venv/bin/python

import discord      # base discord module
import code         # code.interact
import os           # environment variables
import inspect      # call stack inspection
import random
import os
from discord.channel import VoiceChannel       # dumb random number generator

from discord.ext import commands    # Bot class and utils

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
    # user selectable display config (prompt symbol, color)
    dsp_sel = {
        'debug'   : ('\033[34m', '-'),
        'info'    : ('\033[32m', '*'),
        'warning' : ('\033[33m', '?'),
        'error'   : ('\033[31m', '!'),
    }

    # internal ansi codes
    _extra_ansi = {
        'critical' : '\033[35m',
        'bold'     : '\033[1m',
        'unbold'   : '\033[2m',
        'clear'    : '\033[0m',
    }

    # get information about call site
    caller = inspect.stack()[1]

    # input sanity check
    if level not in dsp_sel:
        print('%s%s[@] %s:%d %sBad log level: "%s"%s' % \
            (_extra_ansi['critical'], _extra_ansi['bold'],
             caller.function, caller.lineno,
             _extra_ansi['unbold'], level, _extra_ansi['clear']))
        return

    # print the damn message already
    print('%s%s[%s] %s:%d %s%s%s' % \
        (_extra_ansi['bold'], *dsp_sel[level],
         caller.function, caller.lineno,
         _extra_ansi['unbold'], msg, _extra_ansi['clear']))

################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################

song_list = {
    'bella_ciao.mp3' : '1',
    'the_script_hall_of_fame.mp3' : '2',
    'juanes_la_camisa_negra.mp3' : '3',
    'stromae_alors_on_danse.mp3' : '4',
    'nathan_evans_wellerman.mp3' : '5'
}

# bot instantiation
bot = commands.Bot(command_prefix='!')

# on_ready - called after connection to server is established
@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')

# on_message - called when a new message is posted to the server
#   @msg : discord.message.Message
@bot.event
async def on_message(msg):
    # filter out our own messages
    if msg.author == bot.user:
        return
    
    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')

    # overriding the default on_message handler blocks commands from executing
    # manually call the bot's command processor on given message
    await bot.process_commands(msg)
    #code.interact(local=dict(globals(), **locals())) 

@bot.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    if voice_state is None:
        return 
    if len(voice_state.channel.members) == 1:
        await voice_state.disconnect()

@bot.command(brief='Hai cu melodia!')
# play - play music
async def play(ctx,song):
    if not ctx.message.author.voice:
        await ctx.send("{} Intr?? pe voice dac?? vrei s??-??i c??nt!".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
        await ctx.send("Am ajuns!")
        await channel.connect()
        try :
            server = ctx.message.guild
            voice_channel = server.voice_client
            if song in song_list:
                async with ctx.typing():
                    voice_channel.play(discord.FFmpegPCMAudio(song))
                await ctx.send('**Dedica??ie: **' + song)
            else :
                await ctx.send("Nu ??tiu s?? c??nt asta!")
        except :
            await ctx.send("Am luat pauz?? barosane!")

@bot.command()
async def list(ctx):
    await ctx.send("C??ntece pentru dedica??ie")
    for key in song_list:
        await ctx.send (song_list[key] + '.' + key)


    

    

@bot.command(brief='Ca s?? plece botul')
async def scram(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Gata am plecat!")
    else:
        await ctx.send("Botul nu e disponibil!")


@bot.command(brief='Oprirea dedica??iei')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild= ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("Gata m-am oprit!")
    else:
        await ctx.send("Sunt pe pauz?? momentan!")

@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild= ctx.guild)
    if voice.is_paused():
        voice.resume()
        await ctx.send("Hai s?? continu??m!")
    else:
        await ctx.send("Deja c??nt altceva!")

@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild= ctx.guild)
    voice.stop();        




# roll - rng chat command
#   @ctx     : command invocation context
#   @max_val : upper bound for number generation (must be at least 1)
@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    # argument sanity check
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')

    await ctx.send(random.randint(1, max_val))

# roll_error - error handler for the <roll> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))



################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################

if __name__ == '__main__':
    # check that token exists in environment
    if 'BOT_TOKEN' not in os.environ:
        log_msg('save your token in the BOT_TOKEN env variable!', 'error')
        exit(-1)

    # launch bot (blocking operation)
    bot.run(os.environ['BOT_TOKEN'])
    
    import argparse
 
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--token", help="sends token to the discord bot", action="store_true")
args = parser.parse_args()
if args.verbose:
    print("Token received")
    