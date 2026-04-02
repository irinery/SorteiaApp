# Sistema de Sorteio para Live — Requisitos

THIS PROJECT IS SPEC-DRIVEN.
ALL IMPLEMENTATION MUST FOLLOW requirements.md
DO NOT ADD FEATURES NOT IN THE SPEC.
DO NOT CHANGE UI FLOW.
DO NOT CHANGE STATES.

## Fluxo obrigatório
Selecionar fonte → Selecionar chat → Coletar → Revisar lista → Sortear → Mostrar vencedor

## Estados obrigatórios
- DISCONNECTED
- CONNECTED
- CHAT_SELECTED
- PARTICIPANTS_LOADED
- READY_TO_DRAW
- DRAW_COMPLETED

## Botões obrigatórios
- Conectar
- Selecionar chat
- Coletar participantes
- Sortear
- Sortear novamente
- Reiniciar
- Adicionar participante
- Remover participante
- Limpar lista

## Regras essenciais
- Não sortear sem participantes elegíveis
- Não sortear sem chat selecionado
- Remover duplicados e ignorar nomes vazios
- Manter vencedor visível até novo sorteio
- Permitir copiar vencedor
