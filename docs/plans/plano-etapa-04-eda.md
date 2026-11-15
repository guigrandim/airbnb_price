# Etapa 04: Análise Exploratória de Dados

**Status:** EDA, heatmaps e follow-up de outliers executados em 04/11/2026; gate aguardando aprovação do usuário.

**Objetivo:** descrever os anúncios de treino, investigar cinco relações de negócio com `price` e avaliar redundância entre preditoras.

Revisão V2 executada em 15/11/2026: população ampliada, cinco hipóteses, heatmaps e triagem contextual de preços. Ver [plano e resultados V2](plano-revisao-etapas-02-04-03.md). O conteúdo abaixo registra o baseline histórico; gate V2 pendente.

**Escopo:** usar `df_modeling_features` apenas onde `particao == "treino"` para a EDA. A validação e o teste ficam fora da análise. Investigar outliers e recomendar retenção/remoção; qualquer exclusão do conjunto de modelagem exige evidência, decisão explícita e fallback.

**Base de entrada:** antes da exclusão autorizada, `df_modeling_features` tinha 14.806 linhas e 45 colunas: 12.187 anúncios de treino e 2.619 de validação. O teste permaneceu reservado; a EDA não leu seus valores.

## Estratégia

1. Confirmar que a base de features existe no kernel, filtrar treino e conferir alvo, dimensões e partição.
2. Descrever ausências, faixas, dispersão, assimetria, curtose e valores extremos. Para categorias, mostrar cardinalidade, frequência e proporção. Outliers serão investigados, sem exclusão nesta etapa.
3. Avaliar cinco hipóteses com estatísticas descritivas, teste apropriado e tamanho do efeito. Interpretar resultados como associação, não causalidade.
4. Verificar dependência entre preditoras numéricas e categóricas. Excluir `price`, `id` e `particao` desta análise de redundância; criar heatmaps para Pearson e Cramér V.
5. Revisar os preços sinalizados pelo IQR e extremos de `bathrooms`, `minimum_nights` e `maximum_nights`, usando atributos do anúncio para classificar plausibilidade e possíveis erros.
6. Registrar achados, limites, pendências e o gate da Etapa 04 no notebook e neste plano.

## Hipóteses prioritárias

| Pergunta de negócio | Hipótese exploratória | Método previsto |
|---|---|---|
| O preço anunciado varia conforme o tipo de acomodação? | `price` difere entre valores de `room_type`. | Mediana, intervalo interquartil, Kruskal-Wallis e tamanho do efeito. |
| A localização do anúncio está associada ao preço? | `price` varia entre bairros. | Contagem, mediana e intervalo interquartil por `neighbourhood_cleansed`; Kruskal-Wallis e tamanho do efeito, com ressalva para grupos pequenos. |
| Anúncios com maior capacidade tendem a anunciar diárias mais altas? | `accommodates` tem associação positiva com `price`. | Correlação de Spearman e inspeção gráfica. |
| Anúncios mais próximos do centro mediano da amostra anunciam diárias mais altas? | `distance_to_training_center_km` tem associação negativa com `price`. | Correlação de Spearman e inspeção gráfica. A distância é um proxy definido na Etapa 03. |
| O preço anunciado difere entre superhosts e os demais anfitriões? | `price` difere segundo `is_superhost`. | Medianas, intervalo interquartil, Mann-Whitney e tamanho do efeito. |

Os resultados devem incluir o tamanho dos grupos e o tamanho do efeito. Valores-p não serão usados isoladamente para declarar relevância de negócio.

## Análise multivariada

- Numéricas: matrizes Pearson e Spearman entre preditoras, sem `price`.
- Categóricas: associação entre pares com Cramér V. Registrar cardinalidade e cautela com categorias raras.
- Relatar pares mais associados e comparar com a auditoria da Etapa 03. Associação não implica causalidade nem determina seleção de features.

## Células previstas

No notebook, inserir a seção `## Etapa 04 — EDA` e trabalhar em blocos de uma a três células:

1. `### 04.1 — Verificação univariada`: criar a visão de treino e apresentar tabelas de distribuição numérica e categórica, além de gráficos que ajudem a ler as caudas.
2. `### 04.2 — Verificação bivariada`: apresentar as cinco hipóteses, seus métodos, saídas e interpretações.
3. `### 04.3 — Verificação multivariada`: medir associação entre preditoras numéricas e categóricas, com heatmaps de Pearson e Cramér V, e destacar redundâncias.
4. `### 04.4 — Revisão de outliers`: inspecionar anúncios sinalizados, confrontar preço e extremos de capacidade, banheiros e restrições de estadia com o contexto disponível e recomendar manter ou investigar remoção.
5. `### 04.5 — Verificação final e gate`: resumir achados, limites, pendências e decisão solicitada para avançar à Etapa 05.

Cada célula de código terá comentários diretos. O texto Markdown explicará a pergunta antes da análise e interpretará a saída depois. Não definir funções, classes ou lambdas no notebook.

## Premissas e limites

- `price` será usado como alvo somente nos anúncios de treino.
- A validação e o teste não serão consultados, nem para escolher cortes, grupos ou hipóteses.
- `availability_365` mede noites disponíveis, não ocupação nem reservas.
- A distância da Etapa 03 usa o centro mediano do treino; não representa distância a um centro oficial.
- Diferenças observadas de preço não provam efeito causal nem preço ótimo.
- Se o kernel tiver sido reiniciado, confirmar e reconstruir os objetos de entrada pelas células anteriores, executadas via MCP e em ordem.

## Critérios de aceite

- [x] A fonte da EDA contém somente linhas de treino; contagem e alvo foram conferidos no kernel.
- [x] Saídas univariadas cobrem variáveis numéricas, categóricas e data, ausências, distribuição e valores extremos.
- [x] As cinco hipóteses têm método, tamanho dos grupos, efeito e interpretação.
- [x] A análise multivariada cobre associações entre preditoras numéricas e categóricas, sem incluir `price`.
- [x] A amostra original de EDA permaneceu intacta e a análise não leu valores da validação/teste; depois, uma linha foi removida somente de `df_modeling_features` por decisão explícita do usuário.
- [x] Cada bloco de uma a três células foi executado e sua saída inspecionada via MCP.
- [x] O notebook encerra com achados, limitações, pendências e o gate da Etapa 04.
- [x] O heatmap de Pearson exibe as 34 preditoras numéricas e usa escala divergente fixa de −1 a 1.
- [x] O heatmap de Cramér V exibe os pares entre as 7 preditoras categóricas, com escala de 0 a 1.
- [x] Os outliers de preço e extremos de banheiros e noites foram revisados com contexto por anúncio; recomendações distinguem erros de valores plausíveis ou inconclusivos.
- [x] A decisão do usuário sobre o registro com `maximum_nights = 9.999` foi registrada com fallback reproduzível; demais valores sem erro confirmado permanecem.

## Execução e evidências — 04/11/2026

- A visão usada tem 12.187 anúncios de treino, com preço válido de €8 a €8.500 e 0 ausências nas 42 preditoras: 34 numéricas, 7 categóricas e 1 data (`host_since`). A data contém 2.639 valores distintos entre 2008-09-24 e 2018-11-25, sem ausências ou erros de conversão.
- `price`: mediana €125, máximo €8.500, skew 31, curtose excedente 1.862; 665 (5,46%) foram sinalizados pelo IQR. `bathrooms`: skew 3,13; 2.198 valores foram sinalizados pelo IQR, com quartis concentrados em 1. `maximum_nights`: mediana e Q3 de 1.125, máximo 9.999. A amostra original foi mantida durante a EDA; a exclusão do registro 9.999 ocorreu depois, por decisão explícita do usuário.
- Kruskal-Wallis encontrou diferenças globais por `room_type` (H=2.233,63; `p < 1e-16` por underflow numérico; ε²=0,183) e `neighbourhood_cleansed` (H=1.118,53; `p=1,481e-223`; ε²=0,090). Medianas por tipo: imóvel inteiro €139, quarto privado €85 e compartilhado €75. A mediana dos bairros variou de €69 a €150; grupos pequenos foram destacados.
- Spearman: `accommodates` ρ=0,547; `distance_to_training_center_km` ρ=−0,287. Superhosts e demais anfitriões tiveram mediana €125; Mann-Whitney `p=0,199`, correlação bisserial por postos=0,018.
- Redundância numérica: 8 pares com |Pearson| ≥0,90 e 14 com |Spearman| ≥0,90, igual à contagem da Etapa 03. Os maiores Cramér V (1,00) envolvem features compostas com seus componentes; cruzamentos de alta cardinalidade têm tabelas esparsas.
- Checks finais do kernel passaram: apenas treino, preço válido, grupos de tipos disjuntos e completos, 0 ausências, 5 hipóteses, 561 pares numéricos e 21 pares categóricos. A exclusão posterior do registro autorizado foi verificada separadamente.
- SciPy estava ausente do ambiente `.venv`; foi instalado localmente para os testes estatísticos. `requirements.txt` agora registra Matplotlib 3.10.9 e SciPy 1.15.3.
- Heatmaps executados e inspecionados: Pearson 34×34 com escala −1 a 1; Cramér V 7×7 com escala 0 a 1 e valores anotados. Foram preservadas as matrizes sem `price`, `id` ou `particao`.
- IQR de `price`: Q1 €95, Q3 €175 e limite superior €295; 665 anúncios (5,46%) foram sinalizados. Desses, 642 são imóveis inteiros e 23 quartos privados; 7 anúncios superam €1.000. Os maiores preços foram €8.500 (ID 12213707; apartamento para 2 hóspedes, 1 quarto e 1 banheiro) e €5.040 (ID 29926643; estúdio para 2 hóspedes). Os atributos não confirmam erro de digitação; ambos foram mantidos. O anúncio de €8.500 já tinha decisão anterior de retenção.
- `bathrooms`: 12 anúncios têm valor 0: 9 quartos privados e 3 imóveis inteiros. A mediana de preço é €74 (n=12), ante €125 nos registros com banheiro positivo. Dentro de `room_type`, quartos privados têm medianas €73 (n=9) e €85; imóveis inteiros, €163 (n=3) e €139. Por `property_type`, quartos privados em apartamentos têm mediana €65 (n=5), ante €80; imóveis inteiros em barcos, €106,50 (n=2), ante €180; as demais combinações com zero têm um anúncio cada. Os preços não indicam erro consistente, mas a amostra pequena limita a conclusão. O máximo 5 ocorre em anúncio de hotel com capacidade para 17 hóspedes e 5 quartos. Os dados não distinguem zero real de informação não registrada; os 12 casos foram mantidos.
- `minimum_nights` máximo 1.001; nenhum registro tem `minimum_nights > maximum_nights`. Na amostra original, `maximum_nights` vale 1.125 em 6.110 anúncios (50,1%), 1.124 em 280; acima de 1.125 existem dois anúncios com 1.825 e um com 9.999. O dicionário define `maximum_nights` como limite de estadia configurado, mas não documenta 1.125 ou 9.999 como padrão automático.
- Por decisão explícita do usuário, o anúncio de treino `id=7447773` (`maximum_nights=9999`, `price=€90`, imóvel inteiro/apartamento) foi removido de `df_modeling_features`. Isso não confirma erro na fonte. A linha integral está em `df_excluded_maximum_nights` (1 × 45), com fallback `df_modeling_features = pd.concat([df_modeling_features, df_excluded_maximum_nights]).sort_index()`.
- Verificação final no kernel: `df_modeling_features` ficou com 14.805 × 45, sendo 12.186 de treino e 2.619 de validação. O treino restante é idêntico à amostra de EDA após retirar somente o ID autorizado; a amostra original de EDA permaneceu intacta e nenhuma feature foi alterada. A validação foi contada pelo rótulo da partição, sem análise de seus atributos; o teste não foi consultado.

**Decisão:** manter os extremos de preço, os 12 registros com `bathrooms=0` e os casos com `maximum_nights=1825`. Excluir somente `id=7447773` do conjunto de modelagem por decisão do usuário, mantendo a linha para fallback. Associação não é causalidade; valores-p, IQR e Cramér V em tabelas esparsas exigem contexto. Redundâncias ficam para comparação posterior.

**Estado do gate:** aguardando aprovação do usuário para avançar à Etapa 05. Última etapa aprovada: Etapa 03.

## Escopo adicional solicitado e executado — 04/11/2026

- Criados e inspecionados heatmaps de Pearson e Cramér V a partir das matrizes calculadas no treino.
- Revisados os 665 preços sinalizados pelo IQR e os extremos de `bathrooms`, `minimum_nights` e `maximum_nights`, com contexto sem consultar validação ou teste.
- Preços extremos e os 12 casos de `bathrooms=0` foram mantidos; a comparação não indicou erro consistente, mas a semântica dos zeros continua incerta.
- `id=7447773` com `maximum_nights=9999` foi retirado apenas de `df_modeling_features` por autorização do usuário; a linha completa e o fallback estão registrados no notebook.
- O conjunto de modelagem ficou com 14.805 × 45 (12.186 treino, 2.619 validação); a amostra original de EDA não mudou. Nenhuma feature foi alterada e o teste não foi consultado.
- A Etapa 04 está concluída; o gate para avançar à Etapa 05 aguarda aprovação do usuário.

**Gate:** ao concluir, pedir literalmente: **“Você aprova a Etapa 04 para avançarmos à Etapa 05?”**

**Notebook:** `notebooks/price_prediction.ipynb`.

## Follow-up autorizado — 04/11/2026

- Excluído de `df_modeling_features` o anúncio de treino `id=7447773`, com `maximum_nights=9999`, por decisão explícita do usuário; a exclusão não foi tratada como comprovação de erro no dado.
- Linha integral preservada em `df_excluded_maximum_nights`; o comando de fallback foi registrado no notebook.
- Comparados os 12 anúncios de treino com `bathrooms=0` por `room_type`, `property_type` e `price`; nenhum padrão de preço confirma erro. Os 12 foram mantidos, reconhecendo que zero pode significar valor real ou informação não registrada.
- Contagens e integridade atualizadas: 14.805 × 45 no conjunto de modelagem, com 12.186 treino e 2.619 validação; amostra de EDA intacta. O teste não foi consultado.
