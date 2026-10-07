import json,pytest
from harness import load
@pytest.fixture
def e(): return load('quote_quorum.py','QuoteQuorum','feeds')
@pytest.mark.parametrize('count,values,expected',[
 (3,[100.0,101.0,99.0],100.0),
 (4,[100.0,102.0,98.0,101.0],100.5),
 (5,[100.25,100.75,99.5,100.0,101.0],100.25),
])
def test_consistent_receipt_supports_three_four_and_five_sources(e,count,values,expected):
 _,c,q,b,U=e
 hosts='abcdefghijklmnopqrstuvwxyz'
 src=json.dumps([{'url':f'https://{hosts[i]}.example/q','path':['price']} for i in range(count)])
 c.register_feed('BTC',src,500)
 b.extend([json.dumps({'price':v}) for v in values]*2)
 c.sample_feed('btc')
 r=json.loads(c.get_feed('0xowner','BTC'))
 assert r['state']=='SAMPLED' and r['status']=='CONSISTENT'
 assert r['median']==expected and r['quotes']==values
 assert r['spread_bps']==pytest.approx((max(values)-min(values))*10000/expected)

def test_outlier_receipt_for_wide_quorum(e):
 _,c,q,b,U=e;src=json.dumps([{'url':f'https://{x}.example/q','path':['price']} for x in 'abcde'])
 c.register_feed('ETH',src,500);values=[100.0,101.0,99.0,100.0,150.0]
 b.extend([json.dumps({'price':v}) for v in values]*2);c.sample_feed('ETH')
 r=json.loads(c.get_feed('0xowner','ETH'))
 assert r['status']=='OUTLIER' and r['median']==100.0 and r['quotes']==values

def test_guards(e):
 _,c,q,b,U=e
 with pytest.raises(U): c.register_feed('BAD','[{"url":"http://a.example","path":["price"]},{"url":"https://b.example","path":["price"]},{"url":"https://c.example","path":["price"]}]',500)
 with pytest.raises(U): c.register_feed('BAD','[{"url":"https://a.example","path":["price"]},{"url":"https://a.example/x","path":["price"]},{"url":"https://c.example","path":["price"]}]',500)
def test_forged_validator_rejected(e):
 _,c,q,b,U=e;src='[{"url":"https://a.example","path":["price"]},{"url":"https://b.example","path":["price"]},{"url":"https://c.example","path":["price"]}]';c.register_feed('BTC',src,500);b.extend(['{"price":100}','{"price":100}','{"price":100}','{"price":100}','{"price":100}','{"price":10000}'])
 with pytest.raises(U): c.sample_feed('BTC')
