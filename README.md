## TelegramTUI
Telegram client on your console

![telegram](https://user-images.githubusercontent.com/18473198/37569384-a4d32e70-2af2-11e8-948c-5a177b384657.png)

### Dependencies
* [Telethon](https://github.com/LonamiWebs/Telethon)
* [NpyScreen](https://github.com/bad-day/npyscreen)
* [python-aalib](http://jwilk.net/software/python-aalib)

### Installation
1. Clone this repository
```bash
git clone https://github.com/IAMVanilka/TelegramTUI.git
```
2. Move to directory
```bash
cd TelegramTUI
```
3. Give the file `run.sh` executable permissions
```bash
chmod +x run.sh
```
4. Run the script
```bash
./run.sh
```

### Proxy
You can set proxy in ```~/.config/telegramtui/telegramtui.ini```

### Controls
* Navigation: `Tab`, `Shift+Tab`, `Mouse`
* Send message: `Ctrl+S`, `Alt+Enter`  
* Delete message: `Ctrl+R`
* Send file: `Ctrl+O`
* Exit: `Ctrl+Q`, `ESC`  
* Copy: `Shift+Mouse`
* Paste: `Shift+Ins`, `Shift+Middle mouse button`
* Emoji menu: `Ctrl+E`
---
## WARNING
I created this fork with AI support, which means there may be some bugs that I haven't spotted.

### Changes in this fork
- The Telethon library has been updated to the latest version.
- The code where Telethon was used has been rewritten to the latest asynchronous code.
- The ability to select emoji has been added. To do this, use "^E".
- The application launch method has been changed.
- Added some shortcut tips at the bottom

The application was tested on **Python 3.12**.