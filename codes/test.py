from toolbox import wrappers
import pandas as pd
import pickle

import datetime
import logging

import os

wkdir = '/net/dali/home/bahar/fangyuan/projects/qsp'
os.chdir(wkdir+'/codes')

file_name = "../data/network/9606.snet.sif"
network = wrappers.get_network(file_name, only_lcc = True, use_edge_data = True)

source_dict = pd.read_csv('../data/network/string_mapping_DrugTargetsHannah.tsv',sep='\t', index_col=1)['stringId']
source = pd.read_csv('../data/network/Both_targets.csv', index_col=0)['Target']
drugs = source.index.tolist()

net_nodes = set(network.nodes())

m1 = pd.read_csv('../data/network/string_mapping_TargetModule_IFN.tsv',sep='\t', index_col=1)['stringId'].tolist()
m2 = pd.read_csv('../data/network/string_mapping_TargetModule_cytokine.tsv',sep='\t', index_col=1)['stringId'].tolist()
module_dict = {
    'IFN':[x for x in m1 if x in net_nodes],
    'Cytokine':[x for x in m2 if x in net_nodes],
}

snodes = module_dict['IFN'] + module_dict['Cytokine']
for drug in drugs:
    nodes_from = [x.strip() for x in source[drug].split(',') if source_dict[x.strip()] in net_nodes]
    nodes_from_ensp = [source_dict[x] for x in nodes_from]  
    snodes.extend(nodes_from_ensp) 
snet = network.subgraph(list(set(snodes)))

def create_logger(logPath=None):
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger("example_logger")
    logger.setLevel(logging.INFO)
    # create the logging file handler
    fh = logging.FileHandler(logPath)
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    return logger


def calc_drug_modules(drug, source=source, source_dict=source_dict, net_nodes=network):    
    
    logPath = wkdir+'/data/netdist/netdist.'+drug+'.log'
    logger = create_logger(logPath)
    logger.info(drug)

    nodes_from = [x.strip() for x in source[drug].split(',') if source_dict[x.strip()] in net_nodes]
    nodes_from_ensp = [source_dict[x] for x in nodes_from]   

    tmp = [] 
    
    if len(nodes_from_ensp)>0 and len(nodes_from_ensp)<30:  
    #     print(datetime.datetime.now().time())  
        for module_name, nodes_to_ensp in module_dict.items():
            try:
                d, z, (mean, sd) = wrappers.calculate_proximity(network, nodes_from_ensp, nodes_to_ensp, min_bin_size = 2, seed=452456, logger=logger)
            except:
                d,z,mean,sd = 0,0,0,0
            tmp.extend([d,z,mean,sd])

        tmp = [drug, nodes_from_ensp] + tmp
        # fname = wkdir+'/data/netdist/netdist.'+drug+'.pkl'
        # with open(fname,'wb') as f:
        #     pickle.dump(tmp, f)
    return tmp


if __name__ == '__main__':

    from multiprocessing import Pool
    num_of_cores = 60
    pool = Pool(num_of_cores)
    # pool.map(test , source.index.tolist())
    # results = []
    # for x in source.index.tolist():
    #     tmp = calc_drug_modules(x)
    #     results.append(tmp)

    results = pool.map(calc_drug_modules, source.index.tolist())
    # print(results)
    fname = wkdir+'/data/netdist/netdist.pkl'
    with open(fname,'wb') as f:
        pickle.dump(results, f)

# results = [pool.apply_async(parzen_estimation, args=(samples, x, w)) for w in widths]
# res_df = pd.DataFrame(data=np.array(res_list), index=source.index, columns=[m+'_'+x for m in module_dict for x in ['d','z','mean','sd']])
