from PIL import Image, ImageTk
import settings


class SpriteManager:
    def __init__(self):
        self.sheet = Image.open(settings.SPRITE_SHEET_PATH).convert("RGBA")
        self.cache = {}

    def get_frames(self, team, unit_kind, action):
        key = (team, unit_kind, action)
        if key in self.cache:
            return self.cache[key]

        coords = settings.SPRITE_MAP[(team, unit_kind)][action]
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
