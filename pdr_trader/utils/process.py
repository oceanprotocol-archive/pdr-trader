from threading import Thread
from pdr_trader.utils.subgraph import get_all_interesting_prediction_contracts
from pdr_trader.utils.contract import PredictorContract
from trade import trade

""" Get all intresting topics that we can predict.  Like ETH-USDT, BTC-USDT """
topics = get_all_interesting_prediction_contracts()
def process_block(block):
    global topics
    """ Process each contract and see if we need to submit """
    print(f"Got new block: {block['number']}...")
    if not topics:
        topics = get_all_interesting_prediction_contracts()
    for address in topics:
        topic = topics[address]
        predictor_contract = PredictorContract(address)
        epoch = predictor_contract.get_current_epoch()
        if epoch > topic['last_submited_epoch']:
            topic['last_submited_epoch'] = epoch
            """ Let's get the prediction and trade it """
            prediction = predictor_contract.get_agg_predval(block['number'])
            if prediction:
                thr = Thread(target=trade, args=(topic,address, prediction,))
                thr.start()
    """ We don't need to wait for threads to finish """
