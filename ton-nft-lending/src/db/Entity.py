from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Nfts(Base):
    __tablename__ = "nfts"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[int] = mapped_column(Integer)
    owner_address: Mapped[str] = mapped_column(String(255))
    received_at: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"Nfts(id={self.id!r}, address={self.address!r}, name={self.name!r}, received_at={self.received_at!r}, owner_id={self.owner_id!r}, owner_address={self.owner_address!r}, status={self.status!r})"


class History(Base):
    __tablename__ = "history"
    id: Mapped[int] = mapped_column(primary_key=True)
    borrower_id: Mapped[int] = mapped_column(Integer)
    borrower_address: Mapped[str] = mapped_column(String(255))
    nft_id: Mapped[int] = mapped_column(ForeignKey("nfts.id"))
    occurred_at: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"History(id={self.id!r}, nft_id={self.nft_id!r}, borrower_id={self.borrower_id!r}, occurred_at={self.occurred_at!r})"


class Configs(Base):
    __tablename__ = "configs"
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[int] = mapped_column(Integer)
    borrow_cost_per_second: Mapped[int] = mapped_column(Integer)
    lend_income_per_second: Mapped[int] = mapped_column(Integer)
    takeback_fee_per_request: Mapped[int] = mapped_column(Integer)
    borrow_duration_in_second: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"Configs(borrow_cost_per_second={self.borrow_cost_per_second!r}, lend_income_per_second={self.lend_income_per_second!r}, takeback_fee_per_request={self.takeback_fee_per_request!r}, borrow_duration_in_second={self.borrow_duration_in_second!r})"
