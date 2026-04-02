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

## Build de executável para Windows (GitHub Actions)

O repositório possui um workflow em `.github/workflows/windows-build.yml` que gera o arquivo `SorteiaApp.exe` com PyInstaller.

### Como usar

1. Faça push do código para uma branch monitorada (`main`, `master` ou `work`) **ou** execute manualmente via **Actions > Build Windows Executable > Run workflow**.
2. Ao término do job, baixe o artefato `SorteiaApp-windows`.
3. Dentro do artefato estará o executável `SorteiaApp.exe`.
