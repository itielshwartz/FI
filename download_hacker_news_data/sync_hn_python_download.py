from hackernews import HackerNews
hn = HackerNews()
def get_last_10_comment():
    m = hn.get_max_item()
    return [hn.get_item(m-i) for i in range(10)]
%timeit -n1 get_last_10_comment()
# loop, best of 3: 8.36 s per loop
