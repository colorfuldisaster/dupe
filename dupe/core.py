import argparse
import collections

import discord


Command = collections.namedtuple('Command', ['name', 'keywords', 'help', 'action'])
CommandResult = collections.namedtuple('CommandResponse', ['message'])
CommandResult.__new__.__defaults__ = ('', )


def put_in_quotes(message):
    return '```' + message + "```"


def get_help(message):
    msg = '\n'.join('command: {}\nkeywords: [{}]\ndescription: {}\n'.format(command.name, command.keywords, command.help) for command in commands)
    msg = put_in_quotes(msg)

    result = CommandResult(message=msg)
    return result


commands = [
        Command('help', ('help', 'how'), 'display actions the bot can perform and the keywords that activate each one', get_help),
        Command('list games', ('game', 'games', 'show', 'list', 'many'), 'display current games', get_help),
]


client = discord.Client()


@client.event
async def on_message(message):
    # We do not want the bot to reply to itself
    if message.author == client.user:
        return

    print('---')
    print('message: {}'.format(message.content))

    # Ignore messages not directed at the bot
    if not (message.channel.is_private or client.user in message.mentions):
        return

    # Set where the bot should reply to
    if message.channel.is_private:
        reply_target = message.author
        reply_target_name = message.author.name
    else:
        reply_target = message.channel
        reply_target_name = message.author.nick

    print('target: {}'.format(reply_target))

    # Count keywords in message
    keyword_counter = collections.Counter()
    for word in message.content.split():
        command_hits = [command for command in commands if word in command.keywords]
        keyword_counter.update(command_hits)

    '''
    command_to_keyboard_hits = [command: len([word for word in message.content.split() if word in command.keywords]) for command in commands]
    mappings = [command for command in mappings if command is not None]
    keyword_counter = collections.Counter(mappings)
    '''

    most_common = keyword_counter.most_common(1)
    if len(most_common) == 0:
        # Couldn't detect a command -- send a generic reply
        msg = 'I don\'t know how to respond to that, {}.  :frowning:'.format(reply_target_name)
        await client.send_message(reply_target, msg)
        return

    (command, hits) = most_common[0]
    print('command_chosen: {} ({} hit(s))'.format(command.name, hits))

    result = command.action(message)
    if isinstance(result, CommandResult):
        await client.send_message(reply_target, result.message)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def parse_args():
    parser = argparse.ArgumentParser(description='dupe game discord bot')
    parser.add_argument('token', help='discord bot token (keep secret)')

    args = parser.parse_args()
    return args


args = parse_args()
client.run(args.token)
