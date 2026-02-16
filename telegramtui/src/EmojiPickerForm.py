from telegramtui.src import npyscreen
from telegramtui.src.emojiGrid import EmojiGrid
from telegramtui.src.config import emoji_menu

class EmojiPickerForm(npyscreen.ActionForm):
    def create(self):
        self.help = None
        self.name = "Emoji Picker"
        self.categories = emoji_menu
        self.category_names = list(self.categories.keys())
        self.current_category = 0

        # ── key bindings ──────────────────────────────────────
        self.add_handlers({
            "^Q": self.on_cancel,
            "^A": self.prev_category,
            "^D": self.next_category
        })

        # ── tabs ─────────────────────────────
        self.tabs = self.add(
            npyscreen.FixedText,
            value=self.build_tabs(),
            editable=False,
            rely=1,
        )

        # ── emoji grid ────────────────────────────────────────
        self.emoji_grid = self.add(
            EmojiGrid,
            rely=3,
            relx=2,
            emojis=[],
        )

        self.load_category()

        #── help ────────────────────────────────────────
        self.help_bottom = self.add(
            npyscreen.FixedText,
            value=self.build_help(),
            editable=False
        )

    # ─────────────────────────────────────────────────────────
    # Tabs
    # ─────────────────────────────────────────────────────────
    def build_tabs(self):
        out = []
        for i, name in enumerate(self.category_names):
            if i == self.current_category:
                out.append(f"[{name}]")
            else:
                out.append(f" {name} ")
        return "  ".join(out)

    def prev_category(self, _):
        self.current_category = (self.current_category - 1) % len(self.category_names)
        self.load_category()

    def next_category(self, _):
        self.current_category = (self.current_category + 1) % len(self.category_names)
        self.load_category()

    def load_category(self):
        name = self.category_names[self.current_category]
        self.tabs.value = self.build_tabs()
        self.emoji_grid.emojis = self.categories[name]
        self.emoji_grid.cursor = 0
        self.display()

    # ─────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────
    def on_ok(self):
        self.help_bottom.rely = 0
        idx = self.emoji_grid.cursor
        if 0 <= idx < len(self.emoji_grid.emojis):
            emoji = self.emoji_grid.emojis[idx]
            self.parentApp.getForm("MAIN").insert_emoji(emoji)

        self.parentApp.switchFormPrevious()
    
    def build_help(self):
        return (
            "← ↑ ↓ →: move | "
            "^A / ^D: category | "
            "Enter: select | "
            "^Q: quit "
        )

    def _resize(self, *args, **keywords):
        super()._resize(*args, **keywords)

        if hasattr(self, "help"):
            self.help_bottom.rely = self.lines - 2
            self.help_bottom.relx = 1

    def on_cancel(self, _=None):
        self.help_bottom.rely = 0
        self.parentApp.switchFormPrevious()

    def beforeEditing(self):
        self.load_category()

    def exit_func(self, _):
        exit(0)
