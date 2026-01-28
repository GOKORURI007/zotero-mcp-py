from pydantic import BaseModel


class AddByIDPayload(BaseModel):
    identifier: str
    collectionKey: str
