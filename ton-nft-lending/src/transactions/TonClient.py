from abc import ABC, abstractmethod
import asyncio
import aiohttp
from tvm_valuetypes import serialize_tvm_stack

from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from tonsdk.provider import ToncenterClient, prepare_address, address_state
from tonsdk.utils import TonCurrencyEnum, to_nano, bytes_to_b64str, Address
from tonsdk.boc import Cell
from tonsdk.contract.token.nft import NFTItem

from ..common.config import (
    toncenter_api_url,
    toncenter_api_key,
    storage_wallet_mnemonics,
)


class AbstractTonClient(ABC):
    @abstractmethod
    def _run(self, to_run, *, single_query=True, delay=0):
        raise NotImplemented

    def get_address_information(
        self, address: str, currency_to_show: TonCurrencyEnum = TonCurrencyEnum.ton
    ):
        return self.get_addresses_information([address], currency_to_show)[0]

    def seqno(self, addr: str, delay=0):
        addr = prepare_address(addr)
        result = self._run(self.provider.raw_run_method(addr, "seqno", []), delay=delay)

        if "stack" in result and (
            "@type" in result and result["@type"] == "smc.runResult"
        ):
            result["stack"] = serialize_tvm_stack(result["stack"])

        return result

    def send_boc(self, boc: Cell):
        return self._run(self.provider.raw_send_message(boc))


class TonCenterTonClient(AbstractTonClient):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.provider = ToncenterClient(
            base_url=toncenter_api_url, api_key=toncenter_api_key
        )

    def _run(self, to_run, *, single_query=True, delay=0):
        try:
            return self.loop.run_until_complete(
                self.__execute(to_run, single_query, delay)
            )

        except Exception as e:  # ToncenterWrongResult, asyncio.exceptions.TimeoutError, aiohttp.client_exceptions.ClientConnectorError
            print(
                "Error while executing TonCenterTonClient._run()"
                " with to_run = %s" % to_run
            )
            print("Exception: %s" % (e))
            raise

    async def __execute(self, to_run, single_query, delay=0):
        if delay > 0:
            await asyncio.sleep(delay)

        timeout = aiohttp.ClientTimeout(total=5)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            if single_query:
                to_run = [to_run]

            tasks = []
            for task in to_run:
                tasks.append(task["func"](session, *task["args"], **task["kwargs"]))

            return await asyncio.gather(*tasks)

    def get_wallet(self, mnemonics: list):
        mnemonics, pub_k, priv_k, wallet = Wallets.from_mnemonics(
            mnemonics=mnemonics,
            version=WalletVersionEnum.v4r2,
            workchain=0,
        )
        return wallet

    def transfer_ton(self, user_address: str, amount: int, delay=0):
        wallet = self.get_wallet(storage_wallet_mnemonics.split())

        seqno_raw_results = self.seqno(wallet.address.to_string(), delay=delay)
        seqno_results = (
            seqno_raw_results[0]["stack"]
            if seqno_raw_results and "stack" in seqno_raw_results[0]
            else []
        )
        seqno_result = seqno_results[0] if len(seqno_results) >= 1 else []
        seqno = (
            int(seqno_result[1], 0)
            if len(seqno_result) >= 2 and seqno_result[0] == "num"
            else 0
        )

        query = wallet.create_transfer_message(
            to_addr=user_address,
            amount=amount,
            seqno=seqno,
        )

        boc = query["message"].to_boc(False)
        self.send_boc(boc)

        # print(f"Base64boc to transfer the TON: {boc}")
        print(f"Transfer Toncoins to {user_address} done, seqno: {seqno}")
        return seqno + 1  # next seqno

    def transfer_nft(self, user_address: str, nft_address: str, delay=0):
        wallet = self.get_wallet(storage_wallet_mnemonics.split())

        body = NFTItem().create_transfer_body(new_owner_address=Address(user_address))

        seqno_raw_results = self.seqno(wallet.address.to_string(), delay=delay)
        seqno_results = (
            seqno_raw_results[0]["stack"]
            if seqno_raw_results and "stack" in seqno_raw_results[0]
            else []
        )
        seqno_result = seqno_results[0] if len(seqno_results) >= 1 else []
        seqno = (
            int(seqno_result[1], 0)
            if len(seqno_result) >= 2 and seqno_result[0] == "num"
            else 0
        )

        query = wallet.create_transfer_message(
            to_addr=nft_address,
            amount=to_nano(0.055, "ton"),
            seqno=seqno,
            payload=body,
        )

        # print(seqno)
        boc = query["message"].to_boc(False)
        self.send_boc(boc)

        # print(
        #     f"Base64boc to transfer the NFT item: {bytes_to_b64str(query['message'].to_boc(False))}"
        # )
        print(f"Transfer NFT item to {user_address} done, seqno: {seqno}")
        return seqno + 1  # next seqno
