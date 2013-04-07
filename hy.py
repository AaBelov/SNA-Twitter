#!/usr/bin/env python
# encoding: utf-8
"""
LJ_fetch.py

Created by Maksim Tsvetovat on 2011-04-28.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import networkx as net
import urllib
import json
from networkx.readwrite import json_graph
import http_server

def sorted_map(map):
    res=sorted(map.iteritems(), key=lambda (k,v): (-v,k))
    return res

def read_tw_friends(g, name):
    response=urllib.urlopen('https://api.twitter.com/1/followers/ids.json?cursor=-1&user_id='+name)
    lines=response.readlines()      
    start=lines[0].find('[')
    end=lines[0].find(']')
    id_block=lines[0][start+1:end]
    ids=id_block.split(',')
    for id in ids:
        g.add_edge(name,id)


def read_lj_friends(g, name):
    # fetch the friend-list from LiveJournal
    response=urllib.urlopen('http://www.livejournal.com/misc/fdata.bml?user='+name)
    for line in response.readlines():
        #Comments in the response start with a '#'
        if line.startswith('#'): continue 
        
        # the format is "< name" (incoming) or "> name" (outgoing)
        parts=line.split()
        
        #make sure that we don't have an empty line
        if len(parts)==0: continue
        
        #add the edge to the network
        if parts[0]=='<': 
            g.add_edge(parts[1],name)
        else:
            g.add_edge(name,parts[1])

def snowball_sampling(g, center, max_depth=3, current_depth=0, taboo_list=[]):
    # if we have reached the depth limit of the search, bomb out.
    #print center, current_depth, max_depth, taboo_list
    if current_depth==max_depth: 
    #    print 'out of depth'
        return taboo_list
    if center in taboo_list:
    #    print 'taboo' 
        return taboo_list #we've been here before
    else:
        taboo_list.append(center) # we shall never return
    read_lj_friends(g, center)
    
    for node in g.neighbors(center):
        taboo_list=snowball_sampling(g, node, current_depth=current_depth+1, max_depth=max_depth, taboo_list=taboo_list)
    
    return taboo_list
 

def main():
    g=net.Graph()
    #snowball_sampling(g,'navalny')
    #print 'done'
    print 'loading'
    g=net.read_pajek('lj_graph')
    print 'done'
    #find the celebrities
    print 'calculating degrees'
    degrees=net.degree(g)
    s_degrees=sorted_map(degrees)
    res_degrees=s_degrees[0:9]
    print res_degrees
    print 'done'
    #find the gossipmongers
    print 'calculating closeness'
    closeness=net.closeness_centrality(g)
    s_closeness=sorted_map(closeness)
    res_closeness=s_closeness[0:9]
    print res_closeness
    print 'done'
    #find bottlenecks
    print 'calculating betweenness'
    betweenness=net.betweenness_centrality(g)
    s_betweenness=sorted_map(betweenness)
    res_betweenness=s_betweenness[0:9]
    print res_betweenness
    print 'done'
    #for n in g:
    #    g.node[n]['name'] = n
    # write json formatted data
    #d = json_graph.node_link_data(g) # node-link format to serialize
    # write json
    #net.write_pajek(g,'lj_lvl3_graph.net')
    #print 'done'
    #json.dump(d, open('force/lj_graph.json','w'))
    #http_server.load_url('force/force.html')
    #net.draw(g)
    

if __name__ == '__main__':
    main()
