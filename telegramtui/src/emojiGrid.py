from telegramtui.src import npyscreen
import curses

EMOJI_COLS = 8
EMOJI_SPACING = 3


class EmojiGrid(npyscreen.wgwidget.Widget):
    def __init__(self, *args, emojis=None, **kwargs):
        self.emojis = emojis or []
        self.cursor = 0
        super().__init__(*args, **kwargs)

        self.add_handlers({
            curses.KEY_LEFT: self.move_left,
            curses.KEY_RIGHT: self.move_right,
            curses.KEY_UP: self.move_up,
            curses.KEY_DOWN: self.move_down,
        })

    def calculate_area_needed(self):
        rows = (len(self.emojis) + EMOJI_COLS - 1) // EMOJI_COLS
        return rows + 1, EMOJI_COLS * EMOJI_SPACING

    def update(self, clear=True):
        pad = self.parent.curses_pad

        for idx, emoji in enumerate(self.emojis):
            row = idx // EMOJI_COLS
            col = idx % EMOJI_COLS

            y = self.rely + row
            x = self.relx + col * EMOJI_SPACING

            if y >= self.rely + self.height - 1:
                break

            try:
                if idx == self.cursor:
                    pad.addstr(y, x, emoji, curses.A_REVERSE)
                else:
                    pad.addstr(y, x, emoji)
            except curses.error:
                pass

    # ── navigation ────────────────────────────────────────────
    def move_left(self, _):
        if self.cursor > 0:
            self.cursor -= 1
            self.display()

    def move_right(self, _):
        if self.cursor < len(self.emojis) - 1:
            self.cursor += 1
            self.display()

    def move_up(self, _):
        if self.cursor - EMOJI_COLS >= 0:
            self.cursor -= EMOJI_COLS
            self.display()

    def move_down(self, _):
        if self.cursor + EMOJI_COLS < len(self.emojis):
            self.cursor += EMOJI_COLS
            self.display()
