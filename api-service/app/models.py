from pydantic import BaseModel

class Account(BaseModel):
    Id: str
    Name: str
    Classification: str | None = None
    CurrencyRef: dict | None = None
    AccountType: str | None = None
    Active: bool
    CurrentBalance: float