## This is "S.T.A.L.K.E.R Localization Toolbox"
This project is created to ease routine manipulations of working on localization
of S.T.A.L.K.E.R mods.

Primarily it's designed (and tested) to translate mods to Ukrainian language

## Goals (TODO)
Create All-in-one app which will help to produce clean, maintainable, correct
mod localizations with ease, both text and audio.

### Planned features
Infra:
- [x] Add version tracking from PyPI
- [x] Add multilang support
  - [x] Add ukrainian language support
- [x] Add ~/.sltools/config file to store configuration

Text:
- [x] Git integration (check for dirty environment)
  - [ ] Add modified files saving into mirrored directory for non-tracked files
- [x] Bad encoding detection and fixes
- [x] Resolve XML C-style includes [Example here](https://github.com/HalavicH/stalker-localization-toolbox/blob/develop/examples/c-style-xml-includes.md)
- [x] XML formatting and fix. S.T.A.L.K.E.R's XML parser has loose XML validation,
    and swallows files with some tokens not allowed in XML 1.0 specification.
    [Example here](https://github.com/HalavicH/stalker-localization-toolbox/blob/develop/examples/non-standard-xml-fix.md)
- [x] `<text>` entries formatting. Game's XML parser ignores extra spaces and line
    breaks (just like HTML). The only way you can put a line break is to use \n.
    This feature alligns text within text blocks to look alike in the game.
    [Example here](https://github.com/HalavicH/stalker-localization-toolbox/blob/develop/examples/text-entry-formatting.md)
- [x] Analysis for not translated files/text blocks
- [x] Automatic text translation using DeepL.
- [x] Analyze broken patterns/placeholders/colors
  - [x] Save report only with --save option
  - [ ] Compare 2 file reports
  - [ ] Fix broken patterns/placeholders/colors
- [x] Search for duplicate keys
- [x] Capitalize text entries
- [ ] Grammar and typos checkup
- [x] Capitalization of the text blocks
- [ ] Automatic scraping for files you need to translate (if you just start translating) with
    integration with **Mod Organizer 2** mod priority (if you want to translate
    a modpack with all at once)

Audio:
- [ ] Handy operations with audio (using ffmpeg):
    - [ ] Convert to-ogg/to-mp3
    - [ ] Convert to mono
    - [ ] Trim/split audio by second
    - [ ] Trim silence from audio (with user defined margin)
    - [ ] Normalize audio level
- [ ] Apply quick effects (gas mask, radio, pitching, noise)
- [ ] Translating Speech-to-Speech and keeping voice signature using AI   

## Important info
1. All XML files are using `Winodws-1251` encoding, so it's better to setup your
IDE/text editor, git to this encoding by default 
2. A lot of functionality here (like autotranslation) may sometimes introduce
breaking changes like missing/broken placeholder, etc, so it's hardly
recommended to make git repository out of your mod, and commit changes before
each script use (or at least commit often)

## Changelog
## v0.2.0


## v0.1.2
- Add text capitalization command
- Add search for duplicate keys with visualization as D3 graph
- Fix & update broken pattern analysis
  - Improve pattern analysis with --save option
- Fix translation command by "wiring" the source language option


## Module Usage
```shell
sltools
python3 -m sltools
```

### Usage examples
All current and future usage examples are [here](https://github.com/HalavicH/stalker-localization-toolbox/blob/develop/TESTS.md)