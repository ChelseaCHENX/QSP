from __future__ import print_function

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import matplotlib as mpl
from matplotlib import colors
from matplotlib import rcParams
import seaborn as sns


def write_gmt(gdict, fpath):  
    with open(fpath, 'w') as f:
        for key, val in gdict.items():
            val_string = '\t'.join(val)
            f.write('%s\tdesc\t%s\n'%(key, val_string))            
    print('finished writing %d gene sets to %s'%(len(gdict), fpath))
    
def scale_data_5_75(data):
    mind = np.min(data)
    maxd = np.max(data)
    
    if maxd == mind:
        maxd=maxd+1
        mind=mind-1
        
    drange = maxd - mind
    return ((((data - mind)/drange*0.70)+0.05)*100)

def read_gmt(fpath):
    gdict = {}
    
    with open(fpath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            items = line.strip().rstrip().split('\t')
            gset = items[0].lower()
            genes = items[2:]
            gdict[gset] = genes            
    return gdict

def write_gmt(gdict, fpath):  
    with open(fpath, 'w') as f:
        for key, val in gdict.items():
            val_string = '\t'.join(val)
            f.write('%s\thttp\t%s\n'%(key, val_string))            
    print('finished writing %d gene sets to %s'%(len(gdict), fpath))
    
def plot_enrich(data, n_terms=20, title=None, save=False, 
                fontsize=20, dpi=300, fmt='png', width=4, height=None): # 20 terms ~ default figsize
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sb
    from matplotlib import colors
    from matplotlib import rcParams

    # Test data input
    if not isinstance(data, pd.DataFrame):
        raise ValueError('Please input a Pandas Dataframe output by gprofiler.')
        
    if not np.all([term in data.columns for term in ['p_value', 'name', 'intersection_size']]):
        raise TypeError('The data frame {} does not contain enrichment results from gprofiler.'.format(data))
        
    data_to_plot = data.iloc[:n_terms,:].copy()    
    data_to_plot['go.id'] = data_to_plot.index
    

    min_pval = data_to_plot['p_value'].min()
    max_pval = data_to_plot['p_value'].max()
    
    # Scale intersection_size to be between 5 and 75 for plotting
    #Note: this is done as calibration was done for values between 5 and 75
    data_to_plot['scaled.overlap'] = scale_data_5_75(data_to_plot['intersection_size'])
    
    norm = colors.LogNorm(min_pval, max_pval)
    sm = plt.cm.ScalarMappable(cmap="coolwarm", norm=norm)
    sm.set_array([])

    sb.set(style="whitegrid")
    height = data_to_plot.shape[0]*0.4
    rcParams.update({'font.size': fontsize,'figure.figsize':[width,height]})

    path = plt.figure()
    plt.scatter(x='recall', y="name", c='p_value', cmap='coolwarm', 
                       norm=colors.LogNorm(min_pval, max_pval), 
                       data=data_to_plot, linewidth=1, edgecolor="grey", 
                       s=[(i+10)**1.5 for i in data_to_plot['scaled.overlap']])
    
    ax = plt.gca()   
    ax.invert_yaxis()
    
    ax.tick_params(axis='both', which='major', labelsize=15)
    ax.tick_params(axis='both', which='minor', labelsize=8)

    ax.set_ylabel('')
    ax.set_xlabel('Gene ratio', fontsize=20, fontweight='normal')
    ax.xaxis.grid(False)
    ax.yaxis.grid(True)
    if title is not None:
        ax.set_title(title)

    # Shrink current axis by 20%
    box = ax.get_position()
    print('%d terms with height'%data_to_plot.shape[0], 'figsize', path.bbox_inches, 'box',box)
    
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Get tick marks for this plot
    #Note: 6 ticks maximum
    min_tick = np.floor(np.log10(min_pval)).astype(int)
    max_tick = np.ceil(np.log10(max_pval)).astype(int)
    tick_step = np.ceil((max_tick - min_tick)/6).astype(int)
    
    # Ensure no 0 values
    if tick_step == 0:
        tick_step = 1
        min_tick = max_tick-1
    
    ticks_vals = [10**i for i in range(max_tick, min_tick-1, -tick_step)]
    ticks_labs = ['$10^{'+str(i)+'}$' for i in range(max_tick, min_tick-1, -tick_step)]

    #Colorbar
    fig = plt.gcf()
    cbaxes = fig.add_axes([0.8, 0.1, 0.03, 0.3])
    cbar = ax.figure.colorbar(sm, ticks=ticks_vals, shrink=0.5, anchor=(0,0.1), cax=cbaxes)
    cbar.ax.set_yticklabels(ticks_labs)
    cbar.set_label("Adjusted p-value", fontsize=15, fontweight='normal')

    #Size legend
    min_olap = data_to_plot['intersection_size'].min()
    max_olap = data_to_plot['intersection_size'].max()
    olap_range = max_olap - min_olap
    
    #Note: approximate scaled 5, 25, 50, 75 values are calculated
    #      and then rounded to nearest number divisible by 5
    size_leg_vals = [np.round(i/5)*5 for i in 
                          [min_olap, min_olap+(20/70)*olap_range, min_olap+(45/70)*olap_range, max_olap]]
    size_leg_scaled_vals = scale_data_5_75(size_leg_vals)

    
    l1 = plt.scatter([],[], s=(size_leg_scaled_vals[0]+10)**1, edgecolors='none', color='black')
    l2 = plt.scatter([],[], s=(size_leg_scaled_vals[1]+10)**1, edgecolors='none', color='black')
    l3 = plt.scatter([],[], s=(size_leg_scaled_vals[2]+10)**1, edgecolors='none', color='black')
    l4 = plt.scatter([],[], s=(size_leg_scaled_vals[3]+10)**1, edgecolors='none', color='black')

    labels = [str(int(i)) for i in size_leg_vals]

    plt.legend([l1, l2, l3, l4], labels, ncol=1, frameon=False, title_fontsize=20, fontsize=14,
                     handlelength=1, loc = 'upper left', borderpad = 1, labelspacing = .6,
                     handletextpad=2, title='Gene overlap', scatterpoints = 1,  bbox_to_anchor=(-2, 8.2/3), 
                     facecolor='black')

    if save:
        plt.savefig(save, dpi=dpi, format=fmt, bbox_inches='tight')
        
    else:
        plt.show()
        return plt.gca()

def calc_combined_score(input_file="../data/string/9606.protein.links.full.v11.0.txt",
    selected_fields=['coexpression','experiments','database']):


    import os
    import sys

    ##########################################################
    ## This script combines all the STRING's channels subscores
    ## into the final combined STRING score.
    ## It uses unpacked protein.links.full.xx.txt.gz as input
    ## which can be downloaded from the download subpage:
    ##      https://string-db.org/cgi/download.pl
    ##########################################################
     

    if not os.path.exists(input_file):
        sys.exit("Can't locate input file %s" % input_file)

    prior = 0.041

    def compute_prior_away(score, prior):

        if score < prior: score = prior
        score_no_prior = (score - prior) / (1 - prior)

        return score_no_prior

    header = True
    for line in open(input_file):

        if header:
            header = False
            continue
        
        l = line.split()
        
        ## load the line
            
        (protein1, protein2,
         neighborhood, neighborhood_transferred,
         fusion, cooccurrence,
         homology,
         coexpression, coexpression_transferred,
         experiments, experiments_transferred,
         database, database_transferred,
         textmining, textmining_transferred,
         initial_combined) = l


        ## divide by 1000

        neighborhood = float(neighborhood) / 1000
        neighborhood_transferred = float(neighborhood_transferred) / 1000
        fusion = float(fusion) / 1000
        cooccurrence =  float(cooccurrence) / 1000
        homology = float(homology) / 1000
        coexpression = float(coexpression) / 1000
        coexpression_transferred = float(coexpression_transferred) / 1000
        experiments = float(experiments) / 1000
        experiments_transferred = float(experiments_transferred) / 1000
        database = float(database) / 1000
        database_transferred = float(database_transferred) / 1000
        textmining = float(textmining) / 1000
        textmining_transferred = float(textmining_transferred) / 1000
        initial_combined = int(initial_combined)


        ## compute prior away

        neighborhood_prior_corrected                 = compute_prior_away (neighborhood, prior)             
        neighborhood_transferred_prior_corrected     = compute_prior_away (neighborhood_transferred, prior) 
        fusion_prior_corrected                       = compute_prior_away (fusion, prior)             
        cooccurrence_prior_corrected                 = compute_prior_away (cooccurrence, prior)           
        coexpression_prior_corrected                 = compute_prior_away (coexpression, prior)            
        coexpression_transferred_prior_corrected     = compute_prior_away (coexpression_transferred, prior) 
        experiments_prior_corrected                  = compute_prior_away (experiments, prior)   
        experiments_transferred_prior_corrected      = compute_prior_away (experiments_transferred, prior) 
        database_prior_corrected                     = compute_prior_away (database, prior)      
        database_transferred_prior_corrected         = compute_prior_away (database_transferred, prior)
        textmining_prior_corrected                   = compute_prior_away (textmining, prior)            
        textmining_transferred_prior_corrected       = compute_prior_away (textmining_transferred, prior) 

        ## then, combine the direct and transferred scores for each category:

        neighborhood_both_prior_corrected = 1.0 - (1.0 - neighborhood_prior_corrected) * (1.0 - neighborhood_transferred_prior_corrected)
        coexpression_both_prior_corrected = 1.0 - (1.0 - coexpression_prior_corrected) * (1.0 - coexpression_transferred_prior_corrected)
        experiments_both_prior_corrected = 1.0 - (1.0 - experiments_prior_corrected) * (1.0 - experiments_transferred_prior_corrected)
        database_both_prior_corrected = 1.0 - (1.0 - database_prior_corrected) * (1.0 - database_transferred_prior_corrected)
        textmining_both_prior_corrected = 1.0 - (1.0 - textmining_prior_corrected) * (1.0 - textmining_transferred_prior_corrected)

        ## now, do the homology correction on cooccurrence and textmining:

        cooccurrence_prior_homology_corrected = cooccurrence_prior_corrected * (1.0 - homology)
        textmining_both_prior_homology_corrected = textmining_both_prior_corrected * (1.0 - homology)

        ## next, do the 1 - multiplication:

        name_dict = {
        'neighborhood':neighborhood_both_prior_corrected,
        'coexpression':coexpression_both_prior_corrected,
        'experiments':experiments_both_prior_corrected,
        'database':database_both_prior_corrected,
        'textmining':textmining_both_prior_corrected
        }

        combined_score_one_minus = 1
        for field in selected_fields:
            combined_score_one_minus *= 1 - name_dict[field]

        # combined_score_one_minus = (
        #     (1.0 - neighborhood_both_prior_corrected) *
        #     (1.0 - fusion_prior_corrected) *
        #     (1.0 - cooccurrence_prior_homology_corrected) *
        #     (1.0 - coexpression_both_prior_corrected) *
        #     (1.0 - experiments_both_prior_corrected) *
        #     (1.0 - database_both_prior_corrected) *
        #     (1.0 - textmining_both_prior_homology_corrected) ) 

        ## and lastly, do the 1 - conversion again, and put back the prior *exactly once*

        combined_score = (1.0 - combined_score_one_minus)            ## 1- conversion
        combined_score *= (1.0 - prior)                              ## scale down
        combined_score += prior                                      ## and add prior.

        ## round

        combined_score = int(combined_score * 1000)
        print(protein1, protein2, combined_score)


 

