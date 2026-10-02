import json,pytest
from harness import load
@pytest.fixture
def e(): return load('quote_quorum.py','QuoteQuorum','feeds')
def test_consistent_receipt(e):
 _,c,q,b,U=e;src=json.dumps([{'url':'https://a.example/q','path':['price']},{'url':'https://b.example/q','path':['price']},{'url':'https://c.example/q','path':['price']}]);c.register_feed('BTC',src,500);b.extend(['{"price":100}','{"price":101}','{"price":99}']*2);c.sample_feed('btc');r=json.loads(c.get_feed('0xowner','BTC'));assert r['state']=='SAMPLED' and r['status']=='CONSISTENT'
def test_guards(e):
 _,c,q,b,U=e
 with pytest.raises(U): c.register_feed('BAD','[{"url":"http://a.example","path":["price"]},{"url":"https://b.example","path":["price"]},{"url":"https://c.example","path":["price"]}]',500)
 with pytest.raises(U): c.register_feed('BAD','[{"url":"https://a.example","path":["price"]},{"url":"https://a.example/x","path":["price"]},{"url":"https://c.example","path":["price"]}]',500)
def test_forged_validator_rejected(e):
 _,c,q,b,U=e;src='[{"url":"https://a.example","path":["price"]},{"url":"https://b.example","path":["price"]},{"url":"https://c.example","path":["price"]}]';c.register_feed('BTC',src,500);b.extend(['{"price":100}','{"price":100}','{"price":100}','{"price":100}','{"price":100}','{"price":10000}'])
 with pytest.raises(U): c.sample_feed('BTC')
