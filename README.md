# SorteiaApp

Aplicativo desktop (Windows/macOS) para sorteio em lives, com interface única e fluxo linear definido em `requirements.md`.

## Como executar

Pré-requisito: Python 3.10+

```bash
python app.py
```

## Funcionalidades implementadas

- Seleção de fonte (`chat atual`, `chat selecionado`, `lista manual`, `lista importada`)
- Seleção de chat/canal
- Coleta de participantes com remoção de duplicados e ignorando vazios
- Lista com busca, status (elegível/removido), remoção manual e contagem
- Edição manual (adicionar, remover, limpar, remover duplicados, restaurar lista anterior)
- Sorteio aleatório com bloqueio para lista vazia
- Exibição de vencedor com destaque e botão para copiar
- Sortear novamente e reiniciar
- Persistência local da última fonte, chat e lista

## Estados do sistema

- `DISCONNECTED`
- `CONNECTED`
- `CHAT_SELECTED`
- `PARTICIPANTS_LOADED`
- `READY_TO_DRAW`
- `DRAW_COMPLETED`

## Observação

A coleta de chat usa dados simulados locais (mock) para operação offline da ferramenta.
