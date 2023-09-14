from PIL import Image as PIm
from .weights_dto import Weights
from os.path import join

coordinates = {
    '광배근': (117, 241),
    '기립근': (950, 441),
    '대퇴사두': (101, 575),
    '대흉근': (130, 225),
    '둔근': (883, 534),
    '삼두': (0, 275),
    '승모근': (130, 132),
    '이두근': (47, 295),
    '전면어깨': (84, 219),
    '측면어깨': (51, 213),
    '코어': (154, 344),
    '햄스트링': (884, 705),
    '후면어깨': (818, 200),
}

BASE_PATH = 'visualizer/sources'


class ImageGenerator:
    def get_image_suffix(self, calorie: int) -> str:
        val = round(calorie/2) // 100
        return max(val, 0) if val < 0 else min(val, 3)

    def generate(self, weights: Weights) -> PIm.Image:
        base_image_path = join(BASE_PATH, "전체.png")

        base_image = PIm.open(base_image_path)

        weight_dict = weights.model_dump()
        for part, calorie in weight_dict.items():
            suffix = self.get_image_suffix(calorie)
            part_image_path = join(BASE_PATH, f"{part}{suffix}.png")
            part_image = PIm.open(part_image_path)
            base_image.paste(part_image, coordinates[part], part_image)

        return base_image


imageGenerator = ImageGenerator()
