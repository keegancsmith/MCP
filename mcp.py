#!/usr/bin/env python

'''
A program to coordinate entellect challenge tron bots to fight each
other. Named after Master Control Program (MCP) from the Tron movies.
'''

import collections
import itertools
import os
import random
import shlex
import subprocess
import tempfile


class ClientException(Exception):
    pass


_Position = collections.namedtuple('Position', 'x y')
class Position(_Position):
    def __new__(cls, x, y=None):
        # Check if we got a tuple/list
        if y is None:
            x, y = x
        x %= GameState.WIDTH
        q, r = divmod(y, GameState.HEIGHT - 1)
        y = r if q % 2 == 0 else GameState.HEIGHT - 1 - r
        # Polar endpoints
        if y in (0, GameState.HEIGHT - 1):
            x = 0
        return _Position.__new__(cls, x, y)

    def __add__(self, p):
        return Position(self.x + p[0], self.y + p[1])

    def __str__(self):
        return '(%s, %s)' % (self.x, self.y)

    @property
    def at_pole(self):
        return self.y in (0, GameState.HEIGHT - 1)

    def neighbours(self):
        if self.at_pole:
            y = 1 if self.y == 0 else GameState.HEIGHT - 2
            return (Position(i, y) for i in xrange(GameState.WIDTH))
        else:
            deltas = ((0, 1), (1, 0), (-1, 0), (0, -1))
            return itertools.imap(self.__add__, deltas)


class GameState(object):
    WIDTH = 30
    HEIGHT = 30
    VALID_STATES = ('Clear', 'Opponent', 'OpponentWall', 'You', 'YourWall')

    def __init__(self, state, you, opponent):
        self.state = state
        self.you = you
        self.opponent = opponent
        assert state[you] == 'You' and state[opponent] == 'Opponent'

    @staticmethod
    def read(fd):
        '''Parses a game state file from the provided file object `fd`.

        Does a lot of validation on the game state. If anything fails a
        `ClientException` is thrown.'''
        state = {}
        position = {}
        for line in fd:
            line = line.strip().split()
            if not line:
                continue

            if len(line) != 3 or line[2] not in GameState.VALID_STATES:
                raise ClientException('Found an invalid game state line: %s'
                                      % line)

            s = line[2]
            try:
                pos = Position(map(int, line[:2]))
            except ValueError:
                raise ClientException('Found an invalid game state line: %s'
                                      % line)

            if pos in state:
                if pos.at_pole:
                    if state[pos] != s:
                        raise ClientException('Different state at pole %s.'
                                              % pos.y)
                else:
                    raise ClientException('State for %s was repeated' % (pos,))

            state[pos] = s
            position[s] = pos

        if len(state) != GameState.WIDTH * (GameState.HEIGHT - 2) + 2:
            raise ClientException('Game state file is missing entries')

        state_count = collections.defaultdict(int)
        for s in state.itervalues():
            state_count[s] += 1
        if state_count['You'] != 1 or state_count['Opponent'] != 1:
            raise ClientException('You or Opponent state not specified only '
                                  'once.')

        return GameState(state, position['You'], position['Opponent'])

    @classmethod
    def iter_positions(cls):
        ps = itertools.product(xrange(cls.WIDTH), xrange(1, cls.HEIGHT - 1))
        ps = itertools.chain([(0, 0)], ps, [(0, cls.HEIGHT - 1)])
        return itertools.imap(Position, ps)

    def __getitem__(self, pos):
        if not isinstance(pos, Position):
            pos = Position(pos)
        return self.state[pos]

    def __iter__(self):
        return self.state.iteritems()

    def write(self, fd):
        for pos, state in self:
            if pos.at_pole:
                for x in xrange(GameState.WIDTH):
                    fd.write('%d %d %s\r\n' % (x, pos.y, state))
            else:
                fd.write('%d %d %s\r\n' % (pos.x, pos.y, state))

    def flip(self):
        'Return a GameState instance with the opponent and you switched.'
        mapping = {
            'You': 'Opponent',
            'Opponent': 'You',
            'YourWall': 'OpponentWall',
            'OpponentWall': 'YourWall',
            'Clear': 'Clear',
        }
        state = dict((p, mapping[s]) for p, s in self)
        return GameState(state, self.opponent, self.you)

    def neighbours(self, pos):
        '''Generator which returns all positions neighbouring (x, y) which are
        CLEAR.'''
        for p in pos.neighbours():
            if self[p] == 'Clear':
                yield p

    def difference(self, game_state):
        '''Returns a dictionary of all items such that self[key] !=
        game_state[key]'''
        return dict((k, (v, game_state[k])) for k, v in self
                    if v != game_state[k])

    def valid_move(self, new_game_state):
        '''Returns True if new_game_state came from a valid move from the
        current state.'''
        old, new = self.you, new_game_state.you
        if self[new] != 'Clear' or new_game_state[old] != 'YourWall':
            return False
        mod_dist = lambda a, b, m: min((a - b) % m, (b - a) % m)
        dx = mod_dist(old.x, new.x, GameState.WIDTH)
        dy = mod_dist(old.y, new.y, GameState.HEIGHT)
        if dx + dy != 1:
            return False
        diff = self.difference(new_game_state)
        if len(diff) > 2:
            return False
        valid_state_changes = {
            ('Clear', 'You'): new,
            ('You', 'YourWall'): old,
        }
        for pos, state_change in diff.iteritems():
            if valid_state_changes.get(state_change) != pos:
                return False
        return True

    def ascii(self):
        'Returns a multi-line ascii string representation of the state.'
        mapping = {
            'You': 'Y',
            'YourWall': 'y',
            'Opponent': 'O',
            'OpponentWall': 'o',
            'Clear': ' ',
        }
        lines = ['+' + '-' * GameState.WIDTH + '+']
        for y in xrange(GameState.HEIGHT):
            line = ['|']
            line.extend(mapping[self[Position(x, y)]]
                        for x in xrange(GameState.WIDTH))
            line.append('|')
            lines.append(''.join(line))
        lines.append('+' + '-' * GameState.WIDTH + '+')
        return os.linesep.join(lines)


DEFAULT_EXECUTABLE = ['./start.sh', 'start.bat'][os.name == 'nt']


def test_game_state(gs):
    for x in zip(gs.ascii().splitlines(), gs.flip().ascii().splitlines()):
        print('%s  %s' % x)
    print('%s => %s' % (gs.you, list(gs.neighbours(gs.you))))
    print('%s => %s' % (gs.opponent, list(gs.neighbours(gs.opponent))))
    polar = Position(13, GameState.HEIGHT - 1)
    print('%s => %s' % (polar, list(gs.neighbours(polar))))

    from StringIO import StringIO
    buf = StringIO()
    gs.write(buf)
    buf.seek(0)
    gs2 = GameState.read(buf)
    assert gs.difference(gs2) == {}

    moveTo = random.choice(list(gs.neighbours(gs.you)))
    state = dict(gs.state)
    state[moveTo] = 'You'
    state[gs.you] = 'YourWall'
    gs2 = GameState(state, moveTo, gs.opponent)
    assert gs.valid_move(gs2)


def run(command, game_state):
    if command is None:
        # Find the command to run in PWD
        command = DEFAULT_EXECUTABLE

    with tempfile.NamedTemporaryFile() as fd:
        game_state.write(fd)
        fd.flush()

        command = shlex.split(command)
        subprocess.call(command + [fd.name])
        fd.seek(0)
        new_game_state = GameState.read(fd)

        if not game_state.valid_move(new_game_state):
            raise ClientException('Invalid move')
        return new_game_state


def run_local_game(args):
    if args.game_state is None:
        state = dict((p, 'Clear') for p in GameState.iter_positions())
        p1 = random.choice(state.keys())
        p2 = Position(p1.x + GameState.WIDTH / 2, p1.y)
        state[p1] = 'You'
        state[p2] = 'Opponent'
        game_state = GameState(state, p1, p2)
    else:
        with file(args.game_state) as fd:
            game_state = GameState.read(fd)

    turn = 0
    while True:
        os.system(['clear', 'cls'][os.name == 'nt'])
        print(game_state.ascii())
        print

        can_move = lambda p: len(list(game_state.neighbours(p))) > 0
        result = {
            (False, False): 'Tie',
            (True, False): 'Player 1 wins',
            (False, True): 'Player 2 wins',
        }.get((can_move(game_state.you), can_move(game_state.opponent)))
        if result is not None:
            print(result)
            break

        is_player1 = turn % 2 == 0
        player = 'Player 1' if is_player1 else 'Player 2'
        opponent = 'Player 2' if is_player1 else 'Player 1'
        print('Running turn for %s...' % player)
        try:
            if is_player1:
                game_state = run(args.player1, game_state)
            else:
                game_state = run(args.player2, game_state.flip()).flip()
        except ClientException as e:
            print('%s made an illegal move: %s' % (player, e))
            print('%s wins' % opponent)
            break

        turn += 1


def run_remote_game(args):
    raise NotImplementedError('This is future functionality.')


def run_validate(args):
    gs = GameState.read(args.game_state)
    if not args.quiet:
        test_game_state(gs)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.strip())
    subparsers = parser.add_subparsers(title='commands')

    player_help = ('The command to run your player. If not specified '
                   'start.bat or start.sh is executed in the current '
                   'directory.')

    parser_local = subparsers.add_parser('local', help='Run a game locally')
    parser_local.add_argument('--player1', help=player_help)
    parser_local.add_argument('--player2', help=player_help)
    parser_local.add_argument('--game-state',
                              help=('Optionally specify the initial game '
                                    'state. Otherwise one is randomnly '
                                    'generated (excluding walls)'))
    parser_local.set_defaults(func=run_local_game)

    parser_remote = subparsers.add_parser('remote',
                                          help='Take part in a remote game')
    parser_remote.add_argument('--command', help=player_help)
    parser_remote.add_argument('--url', required=True,
                               help='The URL for the game being played.')
    parser_remote.set_defaults(func=run_remote_game)

    parser_validate = subparsers.add_parser('validate',
                                          help='Validates a gamestate file')
    parser_validate.add_argument('game_state', type=argparse.FileType('r'),
                                 help=('A path to the game state file to '
                                       'validate'))
    parser_validate.add_argument('--quiet', action='store_true',
                                 help=('Prevent testing the utility functions '
                                       'and outputting the board'))
    parser_validate.set_defaults(func=run_validate)

    args = parser.parse_args()
    args.func(args)
