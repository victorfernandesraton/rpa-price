import pytest
from unittest import TestCase
from rpa.rpa import AmazonScrapper

_test = TestCase()


@pytest.fixture
def html_amazon_card():
    with open("tests/testdata/card_amazon.html", "r") as f:
        return f.read()


def test_extract_data_from_html(html_amazon_card):
    service = AmazonScrapper()

    result = service.get_data_from_card(html_amazon_card)
    _test.assertIn("Samsung Galaxy A34", result["name"])
    _test.assertIn("B0BXB619GS", result["link"])
