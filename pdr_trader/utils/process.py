from pdr_utils.subgraph import get_all_interesting_prediction_contracts
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
        blocks_per_epoch = predictor_contract.get_blocksPerEpoch()
        blocks_till_epoch_end=epoch*blocks_per_epoch+blocks_per_epoch-block['number']
        print(f"\t{topic['name']} (at address {topic['address']} is at epoch {epoch}, blocks_per_epoch: {blocks_per_epoch}, blocks_till_epoch_end: {blocks_till_epoch_end}")
        if epoch > topic['last_submited_epoch'] and epoch>0:
            topic['last_submited_epoch'] = epoch
            """ Let's get the prediction and trade it """
            prediction = predictor_contract.get_agg_predval(block['number'])
            print(f"Got {prediction}.")
            if prediction:
                trade(topic,address, prediction)
