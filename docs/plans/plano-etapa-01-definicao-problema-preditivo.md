# Plano — Etapa 01: Definição do problema preditivo

## Objetivo

Definir a tarefa, o alvo, a população de referência e a métrica de avaliação para treinar um modelo de regressão que estime o preço anunciado por anúncio.

## Escopo e premissas

- Base principal: `data/raw/listings_details.csv`, com uma linha por anúncio.
- Snapshot: captura de 6–7 de dezembro de 2018, `scrape_id=20181206172549`.
- Alvo: `price`, preço anunciado da diária, interpretado em euros conforme o contrato do projeto.
- Preditores candidatos: características do imóvel e capacidade, localização, anfitrião e reputação. A lista final depende das etapas de qualidade e engenharia de atributos.
- Métrica principal: MAPE calculado somente em preços positivos. MAE, RMSE, viés e resultados por segmento são métricas de apoio.
- O problema é uma regressão transversal sobre o snapshot. Não é uma previsão de preços para 2027 ou para o mercado atual.

## Estratégia executada

1. Formular `X` como atributos disponíveis do anúncio e `y = price`.
2. Confirmar a base principal, a granularidade, a chave e a leitura do alvo.
3. Definir MAPE e as métricas complementares, com a restrição de preço positivo.
4. Registrar limites de interpretação: preço anunciado não comprova preço ótimo, causalidade, reservas ou receita.
5. Encerrar com evidências, decisões, pendências e gate da etapa.

## Células previstas no notebook

- `01.1 — Formulação do problema`
- `01.2 — Métrica de avaliação`
- `01.3 — Critério de aceite`
- `01.4 — Limites da análise`
- `01.5 — Resumo e gate`

## Evidências registradas

- A base tem 20.030 anúncios, 96 colunas e IDs únicos.
- Os 17 campos candidatos conferidos existem na base.
- `price` foi convertido em todas as linhas: 20.028 valores positivos, entre €8 e €8.500, e 2 valores iguais a zero.
- O campo aparece com `$` no arquivo; a auditoria registrou que o símbolo é artefato de exportação, conforme o dicionário do Inside Airbnb consultado.
- A URL de origem e a licença do arquivo histórico continuam pendentes.

## Critérios de aceite e status

- Problema, alvo, snapshot, granularidade, métrica e limites de interpretação estão registrados no notebook.
- A etapa não treina nem compara modelos.
- **Status:** aprovada pelo usuário. É a última etapa aprovada.

## Decisões para as etapas seguintes

- Manter o snapshot de 2018 e tratar `price` como alvo de regressão supervisionada.
- Não usar preços futuros do calendário como preditores.
- Definir a lista de features e as regras de prevenção de vazamento após a auditoria de qualidade.
- Concluir a rastreabilidade da URL e da licença da fonte.

Notebook de referência: [price_prediction.ipynb](../../notebooks/price_prediction.ipynb).
