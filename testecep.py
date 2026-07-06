import httpx
cep = 59960-000
with httpx.Client() as client:
    response = client.get("https://brasilapi.com.br/api/cep/v1/99999999" + cep)

    print("Status:", response.status_code)

    if response.status_code == 200:
        print("CEP encontrado:", response.json())
    elif response.status_code == 404:
        print("CEP não encontrado")
    else:
        print("Erro inesperado")