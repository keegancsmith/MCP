=====
 MCP
=====

A program to orchestrate Entellect Challenge bot matches. The Entellect
Challenge is a Tron AI competition.

Named after Master Control Program (MCP) from the Tron movies. To contribute
back just send a pull request on https://github.com/keegancsmith/MCP or
https://bitbucket.org/keegan_csmith/mcp


Installation
============

The only dependency for MCP is Python 2.7 (although it may work on Python
3.x). Just run ``./mcp.py``. Alternatively you can install the script with
distutils. Just run ``python setup.py install`` in the current directory. A
program called ``mcp`` should then be on your ``$PATH``.


Usage
=====

To run against a random AI run::

  $ mcp local --player1 '/path/to/your/ai' --player2 'mcp ai random'

You can adjust *player1* and *player2* accordingly. The default command to run
for a player is ``start.sh`` or ``start.bat`` (depending if you are on a UNIX
variant or not).

MCP has other functionality. Pass ``--help`` to the command to find out more::

  $ mcp --help
  $ mcp remote --help

http://mcpweb.carruthers.za.net/ is a website which allows remote
games. Create a new game then get your player URL for that game. You can then
play in that game with MCP::

  $ mcp remote http://mcpweb.carruthers.za.net/game/1/bgtmKbl4Z2/

The "/bgtmKbl4Z2/" in the URL is a random private identifier which identifies
you for that game. Your opponent will have a different identifier.
