from typing import Sequence, List, Optional
from pydantic import BaseModel,Field

class AddPrinter(BaseModel):
    serial:Optional[str] = None
    model: Optional[str] = None
    print_name:Optional[str] = None
    inv_num: Optional[str] = None
    url: str = Field()
    port: int = Field(default=9100)
    location: Optional[str] = None
    in_use: int= Field(default=1)