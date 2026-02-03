import argparse
import asyncio
from app.services.aggregator_service import AggregatorService
from app.validators import validate_query_input


async def run(query: str):
    validation = validate_query_input(query)
    if not validation:
        print(f"[!] Alvo inválido: {query}")
        return

    normalized_query, query_type = validation

    print(f"[+] Tipo de alvo: {query_type}")
    print(f"[+] Alvo normalizado: {normalized_query}")
    print("[*] Coletando informações passivas...\n")

    service = AggregatorService()
    result = await service.aggregate_query(normalized_query)
    await service.close()

    data = result.model_dump()

    print("========== RESULTADO DE RECON ==========")
    print(f"Alvo: {normalized_query}")
    print(f"Risco: {data.get('risk_level', 'unknown')}")

    # --- GEOLOCALIZAÇÃO ---
    sources = data.get("sources", {})

    geo = sources.get("ipinfo") or sources.get("ipapi")

    if geo:
        print(f"País: {geo.get('country', 'desconhecido')}")
        if geo.get("city"):
            print(f"Cidade: {geo.get('city')}")
    else:
        print("País: desconhecido")

    # --- REDE ---
    network = data.get("network", {})
    print(f"ASN: {network.get('asn', 'N/A')}")
    print(f"Org: {network.get('org', 'N/A')}")

    # --- SEGURANÇA ---
    security = data.get("security", {})
    print(f"VPN/Proxy: {security.get('is_vpn', 'N/A')}")

    # --- ABUSO ---
    abuse = data.get("abuse", {})
    print(f"Abuso reportado: {abuse.get('total_reports', 0)}")

    print("=======================================")


def main():
    parser = argparse.ArgumentParser(
        description="Passive Recon Tool - Whois & IP Info Aggregator"
    )
    parser.add_argument("target", help="IP ou domínio alvo")

    args = parser.parse_args()
    asyncio.run(run(args.target))


if __name__ == "__main__":
    main()
