pacmimi: Arch Linux Pacman mirrorlist merging utility |aur-badge| |pypi-badge|
==============================================================================

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

Install on Arch Linux
+++++++++++++++++++++

On Arch Linux, I provide an `AUR package`_ called ``pacmimi``.

Please refer to the `AUR page on the Arch Linux wiki`_ for help on how to use
the AUR.

An example installation command might be::

    paru -S pacmimi

Install using pip
+++++++++++++++++

You can also `pip`_ to install *pacmimi* only for your own user, e.g.::

    pip install --user pacmimi

.. note::

    *pacmimi* requires Python 3.

GPG-signed Git release tags
+++++++++++++++++++++++++++

From version 1.1.1 and newer, all Git release tags such as ``v1.1.1`` are
signed with the following GPG key:

- User ID: ``Tilman Blumenbach <tilman+git@ax86.net>``
- Fingerprint: ``B67BD719C23DC2A403E15EB102DE477F6DDE8B17``
- Download: Use any major PGP keyserver or
  https://www.ax86.net/attachments/pgp-key.asc

Quick start
-----------

1. Execute the following command::

    sudo pacmimi -s /etc/pacman.d/mirrorlist*
2. This will merge your ``mirrorlist`` and ``mirrorlist.pacnew`` files and
   remove ``mirrorlist.pacnew`` when it's done. It backups the original
   ``mirrorlist`` to ``/etc/pacman.d/_orig_mirrorlist`` before modifying it.

See ``pacmimi -h`` for available options. The ``-s`` (``--sane-defaults``)
option used above enables useful default options.

Version history
---------------

Version 1.1.2
+++++++++++++

- Update README to include AUR package information.

This is really just a release intended to update the README on PyPI, and should've been part of v1.1.1...

Version 1.1.1
+++++++++++++

- GPG-sign Git release tags.

Version 1.1.0
+++++++++++++

- Build process modernization.

Version 1.0.0
+++++++++++++

- First release on PyPI.


.. _pacman package manager: https://www.archlinux.org/pacman/
.. _AUR package: https://aur.archlinux.org/packages/pacmimi
.. _AUR page on the Arch Linux wiki:
    https://wiki.archlinux.org/title/Arch_User_Repository
.. _pip: https://pypi.python.org/pypi/pip


..
    NB: Without a trailing question mark in the following image URL, the
    generated HTML will contain an <object> element instead of an <img>
    element, which apparently cannot be made into a link (i. e. a
    "clickable" image).

.. |pypi-badge| image:: https://img.shields.io/pypi/v/pacmimi.svg?
    :alt:
    :align: middle
    :target: https://pypi.python.org/pypi/pacmimi


.. |aur-badge| image:: https://img.shields.io/aur/version/pacmimi
    :alt:
    :align: middle
    :target: https://aur.archlinux.org/packages/pacmimi


.. vim: tw=120
