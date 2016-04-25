pacmimi: An Arch Linux Pacman mirrorlist merging utility
========================================================

*pacmimi* is an utility to merge two files in the ``mirrorlist`` format
used by the `pacman package manager`_ into a single file.

Use case
--------

A concrete use case for such an utility is the following:

- The `pacman package manager`_ uses a ``mirrorlist`` file containing
  available package mirrors. That file is provided and updated by the
  Arch Linux package ``pacman-mirrorlist``.
- The ``mirrorlist`` file *needs* to be edited by the user in order
  to enable (uncomment) at least one mirror. Personally, I enable
  multiple mirrors and change their order so that faster mirrors come
  first.
- When the ``pacman-mirrorlist`` package is updated, ``pacman`` won't override
  the ``mirrorlist`` file with the updated version if it has been edited
  by the user (which will always be the case). Instead, the new version
  is saved as ``mirrorlist.pacnew``.
- The user thus needs to manually compare both ``mirrorlist`` files and merge
  the changes from the new ``mirrorlist.pacnew`` file into his locally modified
  copy of ``mirrorlist`` while keeping his modifications.
- An easy way to do this is to just replace the local copy with the updated
  ``mirrorlist`` and enable and reorder the correct mirrors all over again, but
  that gets tedious fast.

The last point is where *pacmimi* comes in. *pacmimi* relieves you of that
tedious work -- it removes mirrors which are not available anymore from your
local ``mirrorlist`` and adds newly added mirrors as disabled (commented)
entries. At the same time, it keeps your enabled mirrors and their order
(it will, however, remove those enabled mirrors which are not present
anymore in the new ``mirrorlist``).

Installation
------------

To install *pacmimi*, use `pip`_::

    pip install pacmimi

.. note::

    *pacmimi* requires Python 3.

Quick start
-----------

1. Execute the following command::

    sudo pacmimi -s /etc/pacman.d/mirrorlist*
2. This will merge your ``mirrorlist`` and ``mirrorlist.pacnew`` files and remove
   ``mirrorlist.pacnew`` when it's done. It backups the original ``mirrorlist`` to
   ``/etc/pacman.d/_orig_mirrorlist`` before modifying it.

See ``pacmimi -h`` for available options. The ``-s`` (``--sane-defaults``) option used
above enables useful default options.


.. _pacman package manager: https://www.archlinux.org/pacman/
.. _pip: https://pypi.python.org/pypi/pip