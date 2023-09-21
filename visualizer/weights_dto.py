from pydantic import BaseModel


class Weights(BaseModel):
    광배근: int = 0
    기립근: int = 0
    대퇴사두: int = 0
    대흉근: int = 0
    둔근: int = 0
    삼두: int = 0
    승모근: int = 0
    이두근: int = 0
    전면어깨: int = 0
    측면어깨: int = 0
    코어: int = 0
    햄스트링: int = 0
    후면어깨: int = 0
