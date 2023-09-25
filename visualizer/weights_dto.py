from pydantic import BaseModel


class Weights(BaseModel):
    광배근: float = 0
    기립근: float = 0
    대퇴사두: float = 0
    대흉근: float = 0
    둔근: float = 0
    삼두: float = 0
    승모근: float = 0
    이두근: float = 0
    전면어깨: float = 0
    측면어깨: float = 0
    코어: float = 0
    햄스트링: float = 0
    후면어깨: float = 0
