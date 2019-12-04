import pytest

# Demo for Parametrizing fixtures with class

@pytest.fixture(scope='class')
def demo1(request):
    print('fixture demo1')

@pytest.mark.usefixtures('demo1')
@pytest.mark.parametrize('a', [1, 2])
@pytest.mark.parametrize('b', [3, 4])
class Test1(object):
    '''
    demo1 run once, will generate 8 cases
    '''
    def test1(self, a, b):
        print('test 1-1', a, b)

    def test2(self, a, b):
        print('test 1-2', a, b)


@pytest.fixture(scope='class')
def demo2(request):
    print('fixture demo2', request.param)

@pytest.mark.parametrize('demo2', [1, 2], indirect=True)
@pytest.mark.parametrize('b', [3, 4])
class Test2(object):
    '''
    fixture with params, demo2 run twice, will generate 8 cases
    '''
    def test1(self, demo2, b):
        print('test 2-1', b)

    def test2(self, demo2, b):
        print('test 2-2', b)

@pytest.fixture(scope='class')
def demo_a(request):
    return request.param

@pytest.fixture(scope='class')
def demo_b(request):
    return request.param

@pytest.mark.parametrize('demo_a', [1, 2], indirect=True)
@pytest.mark.parametrize('demo_b', [3, 4], indirect=True)
class Test3(object):
    '''
    fixture with multiple params, demo3 run 4 times, will generate 8 cases
    '''
    @pytest.fixture(scope='class', autouse=True)
    def demo3(self, demo_a, demo_b):
        print('fixture demo3', demo_a, demo_b)

    def test1(self):
        print('test 3-1')

    def test2(self):
        print('test 3-2')

@pytest.fixture()
def demo_c(request):
    return request.param

@pytest.fixture()
def demo_d(request):
    return request.param

@pytest.mark.parametrize('demo_c', [1, 2], indirect=True)
@pytest.mark.parametrize('demo_d', [3, 4], indirect=True)
class Test4(object):
    '''
    fixture with multiple params, demo4 run 8 times, will generate 8 cases
    use with class scope fixture will raise ScopeMismatch error
    due to capfd is function scope
    use `pytest --capture=fd` instead
    '''
    @pytest.fixture(autouse=True)
    def demo4(self, capfd, demo_c, demo_d):
        print('fixture demo3', demo_c, demo_d)
        capfd.readouterr()

    def test1(self):
        print('test 4-1')

    def test2(self):
        print('test 4-2')
