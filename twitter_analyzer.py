# coding=utf-8
import zen
import matplotlib.pyplot as plt
import json
import re
import pyedgelist

## COMMUNITY DETECTION ====================================

#%% Create Hashtag setlist
with open('raw_twitter.json','rb') as fObj:
    raw_twitter = fObj.readlines()
i = 0
for tweet in raw_twitter[1:]:
    i += 1
    tweet_text = (json.loads(tweet)['text']+' ').lower()
    hashtags = re.findall(r'\#(.*?)\ ',tweet_text)
    hashtags = filter(lambda x: x != '',hashtags)
    if len(hashtags) > 0:
        with open('hashtag_sets.txt','ab') as fObj:
            fObj.write(((' '.join(hashtags))+'\n').encode('utf-8'))
            
print '"hashtag_sets.txt" created.'
    
#%% Construct graph from setlist
G = zen.Graph()
with open('hashtag_sets.txt','rb') as fObj:
    hashtag_set = fObj.readlines()

for ht_set in hashtag_set:
    hts = ht_set.strip().split(' ')
    for ht1 in hts:
        for ht2 in hts:
            if ht1 != ht2:
                try:
                    G.add_edge(ht1,ht2,weight=1)
                except zen.exceptions.ZenException:
                    w = G.weight(ht1,ht2) + 1
                    G.set_weight(ht1,ht2,w)
                    
#zen.io.edgelist.write(G,'hashtags.edgelist',use_weights=True) #,use_node_indices=True)
pyedgelist.write(G,'hashtags.edgelist',use_weights=True)
print '"hashtags.edgelist" created.'

#%% Analyze Graph
# Weights listed first on arabic tweets.. because set to write right->left??
#G = zen.io.edgelist.read('hashtags.edgelist',weighted=True)
G = pyedgelist.read('hashtags.edgelist',weighted=True,ignore_duplicate_edges=True)
w=100
c=30000
print 'Graph loaded'
nn= G.num_nodes
print 'Oringinal Number of Nodes: %d'%(nn)
ne = G.num_edges
print 'Oringinal Number of Edges: %d'%(ne)
comps = zen.algorithms.components(G)
small_components = []
for component in comps:
    if len(component) < c:
        small_components.append(component)

for small_component in small_components:
    for node in small_component:
        G.rm_node(node)
print 'After removing small components: %.2f %% reduction in nodes'%((nn-float(G.num_nodes))*100/nn)

for edge in G.edges_():
    if G.weight_(edge) < w:
        G.rm_edge_(edge)
        
for node in G.nodes():
    if len(G.neighbors(node))==0:
        G.rm_node(node)
G.compact()
print 'After setting weight threshold: %.2f %% reduction in edges'%((ne-float(G.num_edges))*100/ne)
print ''
print 'Nodes: %d     Edges: %d'%(G.num_nodes,G.num_edges)
#cset = zen.algorithms.community.louvain(G,use_weights=True)
from zen.algorithms.community import louvain
cset = louvain(G)
print 'Number of Communities: %d'%(cset.communities().__len__())
comm_sizes = []
for comm in cset.communities().__iter__():
    comm_sizes.append(comm.__len__())
plt.hist(comm_sizes,20)
plt.xlabel('community sizes')
plt.show()
for comm in cset.communities():
    with open('htag_communities_w%d_c%d.txt'%(w,c),'ab') as fObj:
        fObj.write(' '.join(comm.nodes()))
        fObj.write('\n')
print 'Communities written to "htag_communities_w%d_c%d.txt".'%(w,c)
