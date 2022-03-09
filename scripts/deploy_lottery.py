from email import utils
from webbrowser import get
from scripts.utils import get_account, get_contract, fund_with_link
from brownie import Lottery, network, accounts, config
import time


def deploy_lottery():
    account = get_account()
    # lotto SC need  5 constructor parameter!
    # _priceFeedAddress, -> address of the pricefeed contract
    # address _vrfCoordinator, -> address of the random generator
    # address _link, -> link tokens(used to gas vrf Coordinator)
    # uint256 _fee,
    # bytes32 _keyhash

    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("lottery Deployed!!!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    start_txn = lottery.startLottery({"from": account})
    start_txn.wait(1)
    print("The lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100_000_000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # we can only end when there is funds as a reward of lottery3
    tx = fund_with_link(lottery.address)
    tx.wait(1)

    # call endLottery -> requestRandomness -> fulfillRandomness
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(10)

    print(f"{lottery.recentWinner()} is the Winner !!!!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
