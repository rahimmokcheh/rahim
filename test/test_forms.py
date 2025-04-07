import pytest
import math
def add(a,b):
    return a+b
def test_exemple():
    assert add(8,5)
def test_add():
    assert add(5,-6)
#ajouter des marqueurs (pytest -m square -v)
@pytest.mark.square
def test_square():
    a =25
    assert math.sqrt(a)== 5
@pytest.mark.other
def test_greate():
    m=5
    assert m>=2

#ajouter une fonction de fixation (pytest -k par -v) sous-chaine
@pytest.fixture
def input_value():
    a=40
    return a

def test_divisible_par_3(input_value):
    assert input_value%3 == 0
def test_divisible_par_5(input_value):
    assert input_value % 5 ==0