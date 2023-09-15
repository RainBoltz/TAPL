import time, os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .Entity import Nfts, History, Configs


class Database:
    def __init__(self):
        # create engine
        db_path = os.path.join(os.path.dirname(__file__), "db.sqlite3")
        engine = create_engine(f"sqlite:///{db_path}", echo=True, future=True)

        # create a configured "Session" class
        SessionLocal = sessionmaker(bind=engine, future=True)

        # create a Session
        self.session = SessionLocal()

    def get_last_configs(self):
        return self.session.query(Configs).order_by(Configs.id.desc()).first()

    def get_not_returned_nfts_by_user_id(self, user_id: int):
        user_id = int(user_id)
        return (
            self.session.query(Nfts)
            .filter(Nfts.owner_id == user_id)
            .filter(Nfts.status != "returned")
            .all()
        )

    def get_available_nft_by_nft_address(self, nft_address: str):
        return (
            self.session.query(Nfts)
            .filter(Nfts.address == nft_address)
            .filter(Nfts.status == "available")
            .first()
        )

    def get_nft_by_nft_id(self, nft_id: int):
        nft_id = int(nft_id)
        return self.session.query(Nfts).filter(Nfts.id == nft_id).first()

    def get_nfts_by_status(self, status: str):
        return self.session.query(Nfts).filter(Nfts.status == status).all()

    def add_nft(
        self, address: str, name: str, owner_id: str or int, owner_address: str
    ):
        owner_id = int(owner_id)
        nft = Nfts(
            address=address,
            name=name,
            owner_id=owner_id,
            owner_address=owner_address,
            received_at=int(time.time()),
            status="available",
        )
        self.session.add(nft)
        self.session.commit()

    def update_nft_status_by_address_and_status(
        self, address: str, old_status: str, new_status: str
    ):
        nft = (
            self.session.query(Nfts)
            .filter(Nfts.address == address)
            .filter(Nfts.status == old_status)
            .first()
        )
        if nft:
            nft.status = new_status
            self.session.commit()

    def add_history(self, user_id: int or str, user_address: str, nft_id: str or int):
        nft_id = int(nft_id)
        user_id = int(user_id)
        history = History(
            borrower_id=user_id,
            borrower_address=user_address,
            nft_id=nft_id,
            occurred_at=int(time.time()),
        )
        self.session.add(history)
        self.session.commit()

    def update_nft_status_by_nft_id(self, nft_id: str or int, new_status: str):
        nft_id = int(nft_id)
        nft = self.session.query(Nfts).filter(Nfts.id == nft_id).first()
        if nft:
            nft.status = new_status
            self.session.commit()

    def get_histories_by_nft_id(self, nft_id: int):
        nft_id = int(nft_id)
        return (
            self.session.query(History)
            .filter(History.nft_id == nft_id)
            .order_by(History.occurred_at.desc())
            .all()
        )

    def get_history_by_user_id_and_time_range(
        self, user_id: int, start_time: int, end_time: int
    ):
        user_id = int(user_id)
        return (
            self.session.query(History)
            .filter(History.borrower_id == user_id)
            .filter(History.occurred_at >= start_time)
            .filter(History.occurred_at <= end_time)
            .all()
        )

    def get_latest_history_by_nft_id(self, nft_id: int):
        nft_id = int(nft_id)
        return (
            self.session.query(History)
            .filter(History.nft_id == nft_id)
            .order_by(History.occurred_at.desc())
            .first()
        )

    def get_ongoing_borrowed_nfts_by_user_id_and_time(self, user_id: int, time: int):
        user_id = int(user_id)
        return (
            self.session.query(History)
            .join(Nfts, History.nft_id == Nfts.id)
            .filter(History.borrower_id == user_id)
            .filter(Nfts.status == "borrowed")
            .filter(History.occurred_at >= time)
            .all()
        )

    def get_available_nfts_by_owner_id(self, user_id: int):
        user_id = int(user_id)
        return (
            self.session.query(Nfts)
            .filter(Nfts.owner_id == user_id)
            .filter(Nfts.status == "available")
            .all()
        )
