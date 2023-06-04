# textual-astview ChangeLog

## v0.7.1

**Released: 2023-06-04**

### Changed

- Bumped to `textual-fspicker` v0.0.9.

## v0.7.0

**Released: 2023-06-03**

### Changed

- Moved to using `textual-fspicker` as the way to open a new file for
  viewing.
- Updated to [Textual 0.27.0](https://github.com/Textualize/textual/releases/tag/v0.27.0).

## v0.6.1

**Released: 2023-04-29**

### Fixed

- Fixed a crash when running up with no filename on the command line.

## v0.6.0

**Released: 2023-04-29**

### Changed

- Updated to [Textual 0.22.0](https://github.com/Textualize/textual/releases/tag/v0.22.0).

## v0.5.0

**Released 2023-02-16**

### Changed

- Updated to [Textual 0.11.0](https://github.com/Textualize/textual/releases/tag/v0.11.0).
- Added a "toggle all" option to the tree.
- Added support for sizing the panes, with C-left and C-right.

### Fixed

- `Source` will now scroll horizontally when needed.

## v0.4.1

**Released 2022-12-28**

### Fixed

- `astare` should run with Python 3.8 now (before now it was only good on
  3.9 or later).

## v0.4.0

**Released 2022-12-26**

### Changed

- `astare` can now be run up without giving a filename as a parameter, in
  which case the a file selection tree of the current directory will be
  shown.
- Passing a directory on the command line of `astare` will show a file
  selection tree to start with.

### Fixed

- `astare` should run with Python 3.9 now (before now it was only good on
  3.10 or later).

## v0.3.0

**Released 2022-12-25**

### Added

- Added a simple "rainbow" highlight mode, turned off by default.
- Added support for dark/light mode toggling.
- Added the ability to open a new file to view (albeit using a directory
  browser and only one that can currently see files in the current directory
  and all children -- a more comprehensive file opening system will follow).

### Changed

- Updated to [Textual 0.8.1](https://github.com/Textualize/textual/releases/tag/v0.8.1).
- The source highlight update on changing the selected node is delayed by a
  fraction of a second (currently 0.2 seconds), and is cancelled if the node
  changes within that time. The idea being that it should be faster to move
  through large files if holding a direction key down.
  ([#6](https://github.com/davep/textual-astview/issues/6)).

## v0.2.0

**Released 2022-12-21**

### Added

- Added a `--theme` parameter to `astare` to set the theme for the source
  display.
- Added a `--themes` parameter to `astare` to list the themes available for
  the source display.
- Tweaked the current-AST-node highlight in the source code so that it's a
  bit less eye-achingly horrible. It's still not brilliant, but it's less
  bad. Suggestions welcome.

## v0.1.0

**Released 2022-12-20**

Initial release.

[//]: # (ChangeLog.md ends here)
