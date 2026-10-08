import re,io,glob,collections,sys
from html.parser import HTMLParser
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOID={'meta','link','img','br','input','hr','source','path','circle','rect','line','polyline','use','stop'}
class Node:
    def __init__(s,tag,attrs,parent): s.tag=tag; s.attrs=dict(attrs); s.parent=parent; s.kids=[]  # kids: Node or str
    def cls(s): return s.attrs.get('class','')
    def text(s): return ''.join(k if isinstance(k,str) else k.text() for k in s.kids if not (isinstance(k,Node) and k.tag in('script','style','svg')))
class P(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.root=Node('root',[],None); s.cur=s.root
    def handle_starttag(s,t,a):
        n=Node(t,a,s.cur); s.cur.kids.append(n)
        if t not in VOID: s.cur=n
    def handle_endtag(s,t):
        n=s.cur
        while n and n.tag!=t: n=n.parent
        if n and n.parent: s.cur=n.parent
    def handle_data(s,d): s.cur.kids.append(d)
def scan(path):
    p=P(); p.feed(io.open(path,encoding='utf-8').read()); out=[]
    def walk(n):
        if n.tag in('script','style','svg','head'): return
        ks=n.kids
        for a,b in zip(ks,ks[1:]):
            if isinstance(a,Node) and isinstance(b,Node) and a.tag not in('svg','script','style','br') and b.tag not in('svg','script','style','br'):
                ta,tb=a.text().strip(),b.text().strip()
                if ta and tb: out.append((n.tag,n.cls(),a.tag+'.'+a.cls(),b.tag+'.'+b.cls(),ta[:22],tb[:22]))
        for k in ks:
            if isinstance(k,Node): walk(k)
    walk(p.root); return out
if __name__=='__main__':
    files=[f for f in glob.glob(R+'/**/index.html',recursive=True)+[R+'/index.html'] if not re.search(r'/(inbox|tools|node_modules)/',f)]
    cnt=collections.Counter(); ex={}
    for f in sorted(files):
        for r in scan(f):
            k=r[:4]; cnt[k]+=1; ex.setdefault(k,(f[len(R):],r[4],r[5]))
    for k,n in cnt.most_common(80): print(n,k,ex[k])
    print(len(cnt))
