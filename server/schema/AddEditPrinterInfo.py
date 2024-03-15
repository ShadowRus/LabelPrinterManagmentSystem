from typing import Sequence, List, Optional

class AddPrinter(BaseModel):
    name:str=Field()
    model: str = Field(default = 'label printer')
    description: Optional[str] =None
    name: str = Field()
    host: str = Field()
    port: int = Field(default=9100)
    resolution: Optional[str] = None
    priority: Optional[int]= None