import sys; sys.path.insert(0, '.')
from src.fetchers.makeshop_client_local import get_client

client = get_client()
query = """
query searchProduct($input: SearchProductRequest!) {
    searchProduct(input: $input) {
        products { systemCode productName sellPrice consumerPrice display }
        searchedCount
    }
}"""

result = client.execute_query(query, {'input': {'page': 1, 'limit': 10}})
for p in result['data']['searchProduct']['products']:
    print(f"{p['productName'][:30]:30s} | sell:{p['sellPrice']:>8} | consumer:{str(p['consumerPrice']):>8} | display:{p['display']}")
