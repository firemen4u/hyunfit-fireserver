from pydantic import BaseModel


class Weights(BaseModel):
    광배근: int
    기립근: int
    대퇴사두: int
    대흉근: int
    둔근: int
    삼두: int
    승모근: int
    이두근: int
    전면어깨: int
    측면어깨: int
    코어: int
    햄스트링: int
    후면어깨: int
