from PIL import Image, ImageOps, ImageTk
import settings


class SpriteManager:
    def __init__(self):
        self.sheet = Image.open(settings.SPRITE_SHEET_PATH).convert("RGBA")
        self.cache = {}
        self.title_cache = None
        self.overlay_cache = {}

    def get_frames(self, team, unit_kind, action):
        key = (team, unit_kind, action)
        if key in self.cache:
            return self.cache[key]

        sprite_style = settings.sprite_style(unit_kind)
        coords = settings.SPRITE_MAP[(team, sprite_style)][action]
        source_frames = [self._extract_frame(col, row) for col, row in coords]
        boxes = [frame.getchannel("A").getbbox() for frame in source_frames]

        trimmed_frames = []
        max_w = 1
        max_h = 1
        for frame, bbox in zip(source_frames, boxes):
            if bbox is None:
                trimmed = frame
            else:
                trimmed = frame.crop(bbox)
            trimmed_frames.append(trimmed)
            max_w = max(max_w, trimmed.width)
            max_h = max(max_h, trimmed.height)

        frames = []
        for frame in trimmed_frames:
            normalized = Image.new("RGBA", (max_w, max_h), (0, 0, 0, 0))
            offset_x = (max_w - frame.width) // 2
            offset_y = max_h - frame.height
            normalized.paste(frame, (offset_x, offset_y), frame)

            if team == "raccoons":
                normalized = normalized.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

            new_w = max(1, int(normalized.width * settings.SPRITE_SCALE))
            new_h = max(1, int(normalized.height * settings.SPRITE_SCALE))
            normalized = normalized.resize((new_w, new_h), Image.Resampling.LANCZOS)
            frames.append(ImageTk.PhotoImage(normalized))

        self.cache[key] = frames
        return frames

    def _extract_frame(self, col, row):
        x1 = col * settings.SPRITE_CELL_W
        y1 = row * settings.SPRITE_CELL_H
        x2 = x1 + settings.SPRITE_CELL_W
        y2 = y1 + settings.SPRITE_CELL_H

        padding = settings.SPRITE_CAPTURE_PADDING
        padded_box = (
            max(0, x1 - padding),
            max(0, y1 - padding),
            min(self.sheet.width, x2 + padding),
            min(self.sheet.height, y2 + padding),
        )
        return self.sheet.crop(padded_box)

    def get_title_image(self, width, height):
        if self.title_cache is not None:
            return self.title_cache

        title_art = Image.open(settings.TITLE_ART_PATH).convert("RGBA")
        contained = ImageOps.contain(
            title_art,
            (width, height),
            method=Image.Resampling.LANCZOS,
        )
        canvas = Image.new("RGBA", (width, height), (22, 16, 12, 255))
        offset_x = (width - contained.width) // 2
        offset_y = (height - contained.height) // 2
        canvas.paste(contained, (offset_x, offset_y))
        self.title_cache = ImageTk.PhotoImage(canvas)
        return self.title_cache

    def get_overlay_panel(self, width, height, rgba):
        key = (width, height, rgba)
        if key in self.overlay_cache:
            return self.overlay_cache[key]

        panel = Image.new("RGBA", (width, height), rgba)
        image = ImageTk.PhotoImage(panel)
        self.overlay_cache[key] = image
        return image
