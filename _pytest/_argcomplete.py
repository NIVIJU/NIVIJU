
"""allow bash-completion for argparse with argcomplete if installed
needs argcomplete>=0.5.6 for python 3.2/3.3 (older versions fail
to find the magic string, so _ARGCOMPLETE env. var is never set, and
this does not need special code.

argcomplete does not support python 2.5 (although the changes for that
are minor).

Function try_argcomplete(parser) should be called directly before
the call to ArgumentParser.parse_args().

The filescompleter is what you normally would use on the positional
arguments specification, in order to get "dirname/" after "dirn<TAB>"
instead of the default "dirname ":

   optparser.add_argument(Config._file_or_dir, nargs='*'
                               ).completer=filescompleter

Other, application specific, completers should go in the file
doing the add_argument calls as they need to be specified as .completer
attributes as well. (If argcomplete is not installed, the function the
attribute points to will not be used).

SPEEDUP
=======
The generic argcomplete script for bash-completion
(/etc/bash_completion.d/python-argcomplete.sh )
uses a python program to determine startup script generated by pip.
You can speed up completion somewhat by changing this script to include
  # PYTHON_ARGCOMPLETE_OK
so the the python-argcomplete-check-easy-install-script does not
need to be called to find the entry point of the code and see if that is
marked  with PYTHON_ARGCOMPLETE_OK

INSTALL/DEBUGGING
=================
To include this support in another application that has setup.py generated
scripts:
- add the line:
    # PYTHON_ARGCOMPLETE_OK
  near the top of the main python entry point
- include in the file calling parse_args():
    from _argcomplete import try_argcomplete, filescompleter
   , call try_argcomplete just before parse_args(), and optionally add
   filescompleter to the positional arguments' add_argument()
If things do not work right away:
- switch on argcomplete debugging with (also helpful when doing custom
  completers):
    export _ARC_DEBUG=1
- run:
    python-argcomplete-check-easy-install-script $(which appname)
    echo $?
  will echo 0 if the magic line has been found, 1 if not
- sometimes it helps to find early on errors using:
    _ARGCOMPLETE=1 _ARC_DEBUG=1 appname
  which should throw a KeyError: 'COMPLINE' (which is properly set by the
  global argcomplete script).
"""
from __future__ import absolute_import, division, print_function
import sys
import os
from glob import glob

class FastFilesCompleter:
    'Fast file completer class'
    def __init__(self, directories=True):
        self.directories = directories

    def __call__(self, prefix, **kwargs):
        """only called on non option completions"""
        if os.path.sep in prefix[1:]:
            prefix_dir = len(os.path.dirname(prefix) + os.path.sep)
        else:
            prefix_dir = 0
        completion = []
        globbed = []
        if '*' not in prefix and '?' not in prefix:
            if prefix[-1] == os.path.sep:  # we are on unix, otherwise no bash
                globbed.extend(glob(prefix + '.*'))
            prefix += '*'
        globbed.extend(glob(prefix))
        for x in sorted(globbed):
            if os.path.isdir(x):
                x += '/'
            # append stripping the prefix (like bash, not like compgen)
            completion.append(x[prefix_dir:])
        return completion


if os.environ.get('_ARGCOMPLETE'):
    try:
        import argcomplete.completers
    except ImportError:
        sys.exit(-1)
    filescompleter = FastFilesCompleter()

    def try_argcomplete(parser):
        argcomplete.autocomplete(parser)
else:
    def try_argcomplete(parser): pass
    filescompleter = None
