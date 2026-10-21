# Yoosee Fake Cloud - Home Assistant Add-on

Servidor local Fake Cloud e sumidouro de telemetria multi-porta para câmeras Yoosee e Gwelltimes (processadores Anyka AK3918).

Permite operar suas câmeras em modo 100% isolado da nuvem pública chinesa, respondendo às checagens de conectividade HTTP com `200 OK` e absorvendo os pacotes de keepalive UDP para evitar reinicializações e congelamentos de firmware.

---

## 1. Portas de Rede

O Add-on roda em modo `host_network: true` para responder diretamente nas portas necessárias sem necessidade de mapeamentos complexos de NAT:

| Porta | Protocolo | Função |
|---|---|---|
| **8080** (ou 80) | HTTP (TCP) | Mock de conectividade HTTP (`/connect.action`, `/test`, etc.) retornando `200 OK`. |
| **32100** | UDP | Telemetria / Keepalive de nuvem Anyka |
| **32108** | UDP | Heartbeat Anyka AK3918 |
| **18443** | UDP | P2P Heartbeat Gwelltimes |
| **18800** | UDP | P2P Discovery e controle de status |
| **19800** | UDP | Keepalive de stream P2P |

---

## 2. Instruções de DNS (Interceptação Local)

Para que as câmeras se comuniquem com o Fake Cloud em vez dos servidores chineses na internet, crie regras de resolução DNS local (no **AdGuard Home**, **Pi-hole**, **dnsmasq** ou roteador MikroTik/OpenWrt).

Aponte os seguintes domínios para o **endereço IP do Home Assistant** (onde o add-on está rodando):

```dnsmasq
address=/cloudlinks.cn/<IP_DO_HOME_ASSISTANT>
address=/2cu.co/<IP_DO_HOME_ASSISTANT>
address=/yoosee.cc/<IP_DO_HOME_ASSISTANT>
address=/gwelltimes.com/<IP_DO_HOME_ASSISTANT>
address=/gwell.cc/<IP_DO_HOME_ASSISTANT>
```

### Configuração no AdGuard Home
1. Vá em **Filtros** -> **Reescritas de DNS** (DNS Rewrites).
2. Adicione regras direcionando os domínios:
   - `*.cloudlinks.cn` -> `<IP_DO_HOME_ASSISTANT>`
   - `*.2cu.co` -> `<IP_DO_HOME_ASSISTANT>`
   - `*.yoosee.cc` -> `<IP_DO_HOME_ASSISTANT>`
   - `*.gwelltimes.com` -> `<IP_DO_HOME_ASSISTANT>`
   - `*.gwell.cc` -> `<IP_DO_HOME_ASSISTANT>`

### Redirecionamento da porta HTTP 80 para 8080 (Opcional se a câmera chamar na porta 80)
Se as câmeras tentarem acessar a porta 80 em vez da 8080, você pode criar uma regra no firewall do roteador ou iptables no HA:
```bash
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
```
Ou alterar a opção `http_port` no Add-on para `80` (caso nenhuma outra aplicação no host use a porta 80).

---

## 3. Opções de Configuração do Add-on

- **`http_port`** (padrão: `8080`): Porta TCP onde o servidor HTTP de mock escuta.
- **`reply_ack`** (padrão: `true`): Se ativo, responde a pacotes UDP com um ACK genérico para satisfazer o handshake do firmware.
- **`log_level`** (padrão: `"info"`): Nível de detalhamento dos logs (`debug`, `info`, `warning`, `error`).
