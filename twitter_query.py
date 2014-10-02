import sys, itertools, time
import twitter
import networkx as nx

#twitter keys and shit
api_keys = list()
for k in sys.stdin:
	api_keys.append(k.strip())

#create twitter object
auth = twitter.oauth.OAuth(api_keys[2], api_keys[3], api_keys[0], api_keys[1]) 
tw_api = twitter.Twitter(auth=auth)
g = nx.Graph()

#can definitely do this better :)
removeList = ['and','of','the','a','an','but','because','for', 'is', '&', 'if','it','he','him','her','she','his','hers','to','in','that', 'I', 'My', 'We', 'You', 'They']

# ---- Functions --------
def get_rate_limit(t, call_type):
    if call_type=='trends_place':
        limit = t.application.rate_limit_status()
        return limit['resources']['trends']['/trends/place']['remaining']
    
    elif call_type=='lists_memberships':
        limit = t.application.rate_limit_status()
        return limit['resources']['lists']['/lists/memberships']['remaining']

def get_tweet_data(list_of_statuses):
	tweet = [s['text'] for s in list_of_statuses]
	users = [s['user']['screen_name'] for s in statuses]
	description = [s['user']['description'] for s in statuses]
	hashtags_text = [h['text'] for s in list_of_statuses for h in s['entities']['hashtags']]
	data = {'tweet':tweet, 'hashtags_text':hashtags_text, 'users':users, 'description':description}
	return data

#would like to get this to start working, need to have maxID pulled everytime we pull tweets 
#so prev_results should probably be the dict
def twitter_search(q, c=3, n=5, maxID=0, prev_results={}): 
	if n!=0:
		n -= 1
		if prev_results:
			search_results = tw_api.search.tweets(q=q, count=c)
			maxID = search_results['search_metadata']['max_id']-1
			twitter_search(q,c,n,maxID,search_results['statuses'])
		else:
			search_results = tw_api.search.tweets(q=q, count=c, max_id=maxID)
			prev_results += search_results['statuses']
			twitter_search(q,c,n,maxID,prev_results)
	else:
		return prev_results

def graph_add_node(n):
    if g.has_node(n):
        g.node[n]['weight']+=1
    else:
        g.add_node(n)
        g.node[n]['label'] = n
        g.node[n]['weight'] = 1
            
def graph_add_edge(n1, n2):
    if g.has_edge(n1, n2):
        g[n1][n2]['weight']+=1
    else:
        g.add_edge(n1,n2)
        g[n1][n2]['weight']=1

def getDescriptions(td):
	for k,v in td.items():
		if k =='description':
			for i in v:
				for w in i.lower().split():
					if w not in removeList:
						graph_add_node(w)
				for w1, w2 in itertools.combinations(i.split(),2):
					if w1 not in removeList and w2 not in removeList:
						graph_add_edge(w1, w2)

q = 'common core'
c = 100
num_iterate = 5
search_results = tw_api.search.tweets(q=q, count=c)
statuses = search_results['statuses']

for i in range(num_iterate):
	maxID = search_results['search_metadata']['max_id']-1
	search_results = tw_api.search.tweets(q=q, count=c, max_id=maxID)
	statuses += search_results['statuses']

tweetData = get_tweet_data(statuses)
getDescriptions(tweetData)

print g.number_of_nodes()
print g.number_of_edges()

timestamp = time.time()	

nx.write_gexf(g, '%s_%d_tweet_graph.gexf' % (q,timestamp))
print '%s_tweet_graph.gexf' % q

	
		

