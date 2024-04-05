import os
from dotenv import load_dotenv
import discord
import logging
import random

load_dotenv()

logger = logging.getLogger("discord.roller")

TOKEN = os.getenv("TOKEN")
PREFIX = ";"
COMMAND_HELP = "help"
COMMAND_ROLL = "roll"
COMMAND_ABILITIES = "abilities"

STAGE_COUNT = 0
STAGE_SIZE = 1

HELP_MESSAGE = """
I roll dice. I only have three commands:
**;help** -> You're looking at this.
**;abilities** -> Rolls a set of 6 ability scores. (4d6, drop lowest, take sum)
**;roll** -> Rolls dice. Format is ;roll [x]d[y][a/d].
- x -> number of dice. Defaults to 1.
- y -> size of dice. Defaults to 20
- a/d -> advantage or disadvantage respectively.
All parameters are optional, so here are some examples:
- ;roll 2 -> rolls 2d20
- ;roll a -> rolls 1d20 with advantage
- ;roll d6 -> rolls 1d6
- ;roll -> rolls 1d20
- ;roll 2d6d -> rolls 2 lots of 2d6, picks the lower sum.
"""

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def do_roll(dice_count: int = 1, dice_size: int = 20):
    dice_count = max(1,min(dice_count, 50))
    dice_size = max(2,min(dice_size, 100))
    rolls = []
    total = 0
    for _ in range(dice_count):
        v = random.randrange(1,dice_size+1)
        rolls.append(v)
        total += v
    return total, rolls
    



async def help(message:discord.message.Message):
    await message.channel.send(HELP_MESSAGE)

async def roll(message:discord.message.Message, rollParams: list[str]):
    data = "".join(rollParams)

    dice_count = 1
    dice_size = 20

    stage = STAGE_COUNT
    valueA = ""
    valueB = ""
    advantage = None

    if (len(data) > 0):

        if (len(data) == 1):
            if (data == "a"):
                advantage = True
            elif (data == "d"):
                advantage = False
            else:
                await message.channel.send(f'Unrecognised character {data} in roll string!')
                return
        else:
            while len(data) > 0:
                if (data[0].isdigit()):
                    if (stage == STAGE_COUNT):
                        valueA += data[0]
                    elif (stage == STAGE_SIZE):
                        valueB += data[0]
                    data = data[1:]
                elif (data[0] == " "):
                    data = data[1:]
                elif (data[0] == "d" and stage == STAGE_COUNT):
                    data = data[1:]
                    stage = STAGE_SIZE
                elif (data[0] == "a" or data[0] == "d") and stage == STAGE_SIZE:
                    if (data[0] == "a"):
                        advantage = True
                    else:
                        advantage = False
                    data = data[1:]
                else:
                    await message.channel.send(f'Unrecognised character {data[0]} in roll string!')
                    return
            if (valueA.strip() != ""):
                dice_count = int(valueA)
            else:
                dice_count = 1
            if (valueB.strip() != ""):
                dice_size = int(valueB)
            else:
                dice_size = 20

    outRoll = do_roll(dice_count=dice_count, dice_size=dice_size)       
    if (advantage != None):
        rollA = outRoll
        rollB = do_roll(dice_count=dice_count, dice_size=dice_size)

        if (advantage == True and outRoll[0] < rollB[0]) or (advantage == False and rollB[0] < outRoll[0]):
            outRoll = rollB

        advString = "**disadvantage**"
        if (advantage == True):
            advString = "**advantage**"
        
        
        out = f'**{message.author}** rolled **{dice_count}d{dice_size}** with {advString} and rolled:'
        if (dice_count > 1):
            out += f'\n{rollA[1]} for a total of: **{rollA[0]}**\n{rollB[1]} for a total of: **{rollB[0]}**'
        else:
            out += f' {rollA[1][0]} and {rollB[1][0]}'
        out += f'\n\nFinal Roll: **{outRoll[0]}**'
        
        
        await message.channel.send(out)
        
    else:
        out = f'**{message.author}** rolled **{dice_count}d{dice_size}**'
        if (dice_count > 1):
            out += f' and rolled: {outRoll[1]} for a total of **{outRoll[0]}**.'
        else:
            out += f' and rolled: **{outRoll[0]}**'


        await message.channel.send(out)


async def roll_abilities(message:discord.message.Message):
    abilities = []
    for _ in range(6):
        ability = do_roll(4,6)
        min_roll = 10
        for r in ability[1]:
            if (r < min_roll):
                min_roll = r
        ability = (ability[0]-min_roll, ability[1], min_roll)
        abilities.append(ability)
    
    out = f'**{message.author}** rolled some ability scores (4d6, drop lowest):'
    for r in abilities:
        struck_lowest = False
        roll_list = []
        for a in r[1]:
            if (a == r[2] and not struck_lowest):
                roll_list.append(f'~~{a}~~')
                struck_lowest = True
            else:
                roll_list.append(f'{a}')

        out += f'\n- [{", ".join(roll_list)}] for a total of **{r[0]}**'
    
    await message.channel.send(out)
    

async def handle_command(message: discord.message.Message, data: list[str]):
    command = data[0]

    if (command == COMMAND_HELP):
        await help(message)
    elif (command == COMMAND_ROLL):
        await roll(message, data[1:])
    elif (command == COMMAND_ABILITIES):
        await roll_abilities(message)

@client.event
async def on_ready():
    logger.info(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.CustomActivity("Listening for ;roll, ;abilities or ;help"))


@client.event
async def on_message(message: discord.message.Message):
    if (message.author.bot):
        return

    if message.content.startswith(PREFIX):
        content = message.content[1:]

        data = content.split(" ")
        await handle_command(message, data)

def main():
    client.run(TOKEN)
    


if __name__ == '__main__':
    main()