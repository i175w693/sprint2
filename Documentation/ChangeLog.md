# Change Log

## November 8 (Sprint 2)

### Added

- Total cookies and cookies per click are now displayed with 3 decimal places **(Andrew)**
- Implemented more cookies per click **(Andrew)**
- Added scrolling to the shop **(Andrew)**
- Added dynamic pricing and display to shop upgrades **(Ian)**

### Modified

- Fixed infinite upgrade bug by adding a lock and unlock for upgrades to prevent outpacing the cookie count calculator **(Ian)** 
- Fixed Cookies per click not tracking between saves **(Ian)**
- Fixed cookies per click upgrades not tracking between saves **(Ian)**

## November 7 (Sprint 2)

### Added

- Added sprites into main menu **(Jack)**

## November 6 (Sprint 2)

### Added

- Added new upgrades for auto clickers **(Peter)**
- Added new upgrades for click multipliers **(Andrew)**

### Modified

- Moved shop items to the shop class file **(Peter)**

## November 5 (Sprint 2)

### Added

- Added custom mouse cursor **(Jack)**
- Attempted to integrate button backgrounds, need to fix centering **(Peter)**

## November 4 (Sprint 2)

### Added

- Added offline production **(Peter)**
- Added sprite assets **(Jack)**

## November 3 (Sprint 2)

### Added

- Sprint 2 documentation

## October 27 (Sprint 1)

### Added

- load_game code to populate upgrades_acquired list so that the upgrades are shown after loading a save **(Jack)**
- Documentation for all of the game's files and functions **(Peter)**

### Modified

- handle_shop_click to check if an item is already in upgrades acquired to avoid filling the UI with duplicate upgrades **(Jack)**
- draw_upgrades to display cpc or cps depending on the item **(Jack)**
- Fixed bug when displaying purchased items of a loaded save file **(Peter)**
- Fixed bug when trying to load a save file which doesn't exist **(Peter)**

## October 26 (Sprint 1)

### Added

- Code for showing cookies obtained per click (needs bugfixing to have text last for more than 1 cycle) **(Peter)**
- Limited game to 20 ticks per second to prevent overutilization of resources **(Peter)**
- Cookies per click upgrade **(Peter)**
- Save game functionality **(Peter)**
- Load game functionality **(Peter)**

### Modified

- Changed format of the directory to provide better readability and segmentation of code **(Peter)**
- Split code into multiple files **(Peter)**

## October 24 (Sprint 1)

### Added

- Starter code for Cookie Clicker Implementation **(Ian)**
- Files and folders for documentation for Sprint 1 **(Andrew)**
        \+ Documentation Folder
        \+ Change Log Files
        \+ Person Hours Record Sheet
        \+ Sprint 1 Requirements File
