from pydantic import BaseModel


class Model(BaseModel):
    """Base class for model objects"""

    model_config = {
        "extra" : "allow"
    }
