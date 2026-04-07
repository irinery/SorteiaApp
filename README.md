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

## Testes unitários

Os testes automatizados foram adicionados para cobrir as etapas do fluxo obrigatório do sistema:

1. **Conectar**: garante que o estado sai de `DISCONNECTED` para `CONNECTED`, evitando regressão na entrada do fluxo.
2. **Selecionar chat**: valida bloqueios quando desconectado e confirma a transição para `CHAT_SELECTED` quando há chat válido.
3. **Coletar participantes**: assegura remoção de duplicados e nomes vazios, mantendo a regra essencial de elegibilidade.
4. **Revisar lista** (edição): verifica adição manual, bloqueio de duplicados e remoção lógica de participante.
5. **Sortear**: confirma sorteio somente com chat + elegíveis e atualização correta do vencedor/estado.
6. **Reiniciar**: valida limpeza total de dados de rodada sem quebrar o estado de conexão.

### Motivação de cada teste

- **Conexão e seleção de chat**: proteger as transições iniciais da máquina de estados, que sustentam todo o restante do fluxo.
- **Coleta de participantes**: garantir justiça do sorteio ao eliminar entradas inválidas e repetidas.
- **Edição da lista**: evitar inconsistências de operação manual durante lives (duplicidade, remoções e ajustes em tempo real).
- **Sorteio**: impedir sorteios inválidos e confirmar resultado rastreável no estado `DRAW_COMPLETED`.
- **Reinício**: assegurar repetibilidade da operação para novas rodadas sem resíduos de estado anterior.

Para executar localmente:

```bash
python -m pytest -q
```

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

## Regra para bloquear merge em caso de falha

O workflow agora executa testes unitários antes do build. Se **qualquer teste falhar**, o job `unit-tests` falha e o job de build não é autorizado.

Para bloquear merge de fato no GitHub:

1. Acesse **Settings > Branch protection rules** da branch principal.
2. Marque **Require status checks to pass before merging**.
3. Selecione o check **unit-tests**.

Com isso, nenhum merge será permitido até que todas as falhas sejam resolvidas.
