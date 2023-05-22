from threading import Thread
from pdr_trader.utils.subgraph import get_all_interesting_prediction_contracts
from pdr_trader.utils.contract import PredictorContract
from trade import trade

""" Get all intresting topics that we can predict.  Like ETH-USDT, BTC-USDT """
topics = []
def process_block(block):
    global topics
    """ Process each contract and see if we need to submit """
    if not topics:
        topics = get_all_interesting_prediction_contracts()
    print(f"Got new block: {block['number']} with {len(topics)} topics")
    for address in topics:
        topic = topics[address]
        predictor_contract = PredictorContract(address)
        epoch = predictor_contract.get_current_epoch()
        if epoch > topic['last_submited_epoch'] and epoch>2:
            topic['last_submited_epoch'] = epoch
            """ Let's get the prediction and trade it """
            prediction = predictor_contract.get_agg_predval(block['number'])
            print(f"Got {prediction}.")
            if prediction:
                thr = Thread(target=trade, args=(topic,address, prediction,))
                thr.start()
    """ We don't need to wait for threads to finish """
