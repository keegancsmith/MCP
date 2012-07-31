=====
 MCP
=====

A program to orchestrate Entellect Challenge bot matches. The Entellect
Challenge is a Tron AI competition.

Named after Master Control Program (MCP) from the Tron movies.


Installation
============

The only dependency for MCP is Python 2.7 (although it may work on Python
3.x). Just run ``mcp.py``. Alternatively you can install the script with
distutils. Just run ``python setup.py install`` in the current directory.


Usage
=====

To run against a random AI run::

  $ mcp.py local --player1 '/path/to/your/ai' --player2 'mcp.py randomai'

You can adjust *player1* and *player2* accordingly. The default command to run
for a player is ``start.sh`` or ``start.bat`` (depending if you are on a UNIX
variant or not).

MCP has other functionality. Pass ``--help`` to the command to find out more::

  $ mcp.py --help
  $ mcp.py remote --help
