# Whois & IP Info Aggregator  
### Passive Reconnaissance Tool for Pentesting & OSINT

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Async%20API-009688?style=for-the-badge&logo=fastapi)
![Reconnaissance](https://img.shields.io/badge/Reconnaissance-Passive%20Recon-darkred?style=for-the-badge&logo=target)
![OSINT](https://img.shields.io/badge/OSINT-IP%20%26%20Domain%20Intel-black?style=for-the-badge&logo=search)
![API Integration](https://img.shields.io/badge/API-Integration-green?style=for-the-badge&logo=api)
![Security](https://img.shields.io/badge/Cybersecurity-Recon%20Tool-critical?style=for-the-badge&logo=hackaday)


Ferramenta de **reconhecimento passivo** desenvolvida em **Python**, voltada para a **fase inicial de pentests, bug bounty e investigações OSINT**.

O objetivo do projeto é **agregar informações públicas e reputacionais de IPs e domínios** antes da execução de scans ativos, auxiliando o analista de segurança a **entender o alvo, avaliar riscos e decidir próximos passos**.

> **Nenhuma interação ativa com o alvo é realizada** — apenas coleta de inteligência passiva.

---

## Objetivo do Projeto

Este projeto foi desenvolvido como parte de uma trilha prática de **Ferramentas de Reconhecimento**, complementando:

- Scanner de Portas (Recon Ativo)
- Enumerador de Subdomínios (Recon Semi-Ativo)
- **Whois & IP Info Aggregator (Recon Passivo)** ← *este projeto*

Ele demonstra domínio sobre:
- Coleta de inteligência pública (OSINT técnico)
- Integração de múltiplas fontes externas
- Normalização e correlação de dados
- Avaliação inicial de risco de um alvo

---

## Quando usar esta ferramenta?

Antes de rodar:
- `nmap`
- `masscan`
- `dirsearch`
- `ffuf`
- exploits ou fuzzing

Você deve primeiro perguntar:

> **“Com que tipo de alvo estou lidando?”**

Esta ferramenta responde isso.

---

## Informações Coletadas

A ferramenta agrega dados de múltiplas fontes públicas:

### Geolocalização & Rede
- País
- Cidade
- ASN
- Organização / ISP

### Segurança & Reputação
- Detecção de VPN / Proxy
- Score de abuso
- Histórico de reports (AbuseIPDB)
- Classificação de risco (low / medium / high)

### Fontes Utilizadas
- **IPinfo.io** – ASN, organização, geolocalização
- **IP-API.com** – Dados alternativos de localização
- **AbuseIPDB** – Reputação e histórico de abuso

---

## Exemplo de Uso (CLI – Principal)

### Consultar um IP
```
python3 -m app.cli 8.8.8.8
```

## Saída:
```
========== RESULTADO DE RECON ==========
Alvo: 8.8.8.8
Risco: low
País: US
Cidade: Mountain View
ASN: AS15169
Org: Google LLC
VPN/Proxy: false
Abuso reportado: 0
=======================================
```
## Consultar um domínio
```
python3 -m app.cli google.com
```
ideal para **fingerprinting inicial do alvo**.

## API REST (Uso Secundário)
Além da CLI, o projeto expõe uma API REST para integração com outras ferramentas ou pipelines de segurança.

### Iniciar o servidor
```
uvicorn app.main:app --reload
```

### Documentação automática
- Swagger UI: `http://localhost:8000/docs`
    
-  ReDoc: `http://localhost:8000/redoc`
```
POST /api/v1/query
```
```
{
  "query": "8.8.8.8"
}
```

### Arquitetura
```
Cliente (CLI / API)
        ↓
Validação de Entrada
        ↓
AggregatorService
 ├── IPinfo Service
 ├── IP-API Service
 └── AbuseIPDB Service
        ↓
Normalização + Correlação
        ↓
Resultado Unificado
```

### Stack Técnica
-   **Python 3.10+**
    
-   **FastAPI** (async)
    
-   **Pydantic v2**
    
-   **Requests / HTTPX**
    
-   **SlowAPI (rate limiting)**
    
-   **Logging estruturado**
    

Projeto estruturado seguindo boas práticas de engenharia **sem perder o foco em cibersegurança**.

### Segurança & Boas Práticas

-   ✔️ Validação rigorosa de IPs e domínios
    
-   ✔️ Nenhuma execução remota
    
-   ✔️ Sem scans ativos
    
-   ✔️ Rate limiting
    
-   ✔️ Tratamento seguro de exceções
    
-   ✔️ Logs sem dados sensíveis


----------

## Contribuição

Se você gostou do projeto, não esqueça de:

-   ⭐ Deixar uma estrela no Repositório
    
-    Reportar bugs encontrados
    
-    Sugerir novas funcionalidades
    
-    Fazer um fork e contribuir
    

----------

<div align="center"> <sub> Feito por <strong>Prof. Max Muller - MMVonnSeek</strong> para a comunidade de segurança </sub>

  
  

[![Stars](https://img.shields.io/github/stars/MMVonnSeek/whois-ip-recon?style=social)](https://github.com/MMVonnSeek/whois-ip-recon/stargazers)
[![Forks](https://img.shields.io/github/forks/MMVonnSeek/whois-ip-recon?style=social)](https://github.com/MMVonnSeek/whois-ip-recon/network/members)
[![Follow](https://img.shields.io/github/followers/MMVonnSeek?style=social)](https://github.com/MMVonnSeek)

<a href="https://wa.me/5561986194426?text=Olá%20tudo%20bem%20Max%3F%20Eu%20vim%20pelo%20seu%20repositorio%20do%20github.%20Podemos%20conversar%20sobre%3F" target="_blank">
  <img src="https://img.shields.io/badge/WhatsApp-Fale%20Comigo-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" />
</a>

<br>

  [Voltar ao topo](#-whois-ip-recon)

</div>
