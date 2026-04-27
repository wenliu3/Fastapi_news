

def test_yield():
    a = [1, 2, 3]
    for i in a:
        yield i
        print(i)
    print("结束")

b = test_yield()
# print(next(b))

def test2_yield():
    a = [1, 2, 3]
    yield a
    print("test2_yield结束")

def data():
    d = test2_yield()
    print(next(d))
    return "data结束"

# print(data())

class Test:
    def test(self):
        print("提取成功")



ap = Test()

def test_yield():
    yield ap


if __name__ == '__main__':
    q = test_yield()
    q.test()



