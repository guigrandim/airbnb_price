# Etapa 05 V2 — Seleção de features

Data:15/11/2026. Status: gate05V2 aprovado pelo usuário, Etapa06V2 autorizada. Aprovação preserva as36features e a exclusão do ID20644162.

## Objetivo

Avaliar estabilidade das36candidatas V2 e comparar conjunto completo e estável antes da preparação final. Dados em memória; teste preservado.

## Estratégia e premissas

- Reconstruir limpeza/joins/features após exclusão autorizada do anúncio20644162. Atualizar EDA. Resultados CV anteriores ficam históricos; não compará-los como se fossem da mesma população.
- Boruta no treino, KFold3 shuffle seed42. RF60árvores,profundidade12,folha5,max_iter20; orçamento fixo de triagem, sem tuning. Confirmada em>=2/3folds define estável; nenhuma feature escolhida pela validação.
- Imputação mediana com indicadores e encoder ajustados em cada fold. Agregar indicadores de ausência e níveis onehot à variável original; frequência indica pelo menos um indicador confirmado, favorecendo atributos com muitos níveis, limitação explícita.
- Permutação no holdout de cada fold do treino,3repetições,subamostra determinística de até1200linhas; scorer MAPE. Agregar média/desvio/folds com sinal positivo. Colunas originais permutadas inteiras via pipeline.
- Comparar36features e conjunto estável, se não vazio, com RF fixo no treino completo e uma avaliação na validaçãoV2. Reportar MAPE/MAE/RMSE/viés e com/sem histórico. Teste não avaliado.
- Escolhas prévias V2 foram feitas em treino/CV; permutação é diagnóstico interno, não nested CV nem evidência externa do procedimento completo.

## Células previstas

1. Markdown e auditoria de entrada/versões/hash após reconstrução.
2. Boruta e permutação nos três folds internos.
3. Estabilidade/redundância e comparação validação.
4. Interpretação, conjunto recomendado, limitações e gate.

## Aceite

- IDs únicos e partições inalteradas; anúncio removido ausente; hash teste igual.
- Scalers/imputadores/encoders sem fit na validação ou teste; flags derivadas de price fora das candidatas.
- Saídas dos3folds inspecionadas, estabilidade por variável e permutação original documentadas.
- Subconjunto não inventado se Boruta não confirmar atributos estáveis.
- Comparação justa com mesmo estimador e população; sem avanço06 ou11 sem gate.

## Evidências e gate

- Limpeza, reviews e engenharia reconstruídos via MCP após remoção: baseV2 17.021×38; engenharia17.021×52. Treino14.018,validação3.003; ID20644162 ausente. Originais brutos preservados; resultados de CV anteriores à remoção são históricos.
- Auditoria266:36features (27numéricas/9categóricas), Boruta0.4.3. Listas definidas antes do uso, sem dependência do Boruta histórico.
- Boruta268:3folds,60árvores,max_iter20; indicadores confirmados7/4/4 e tentativos1/2/0; matrizes106/105/107colunas. Tempo164,11s incluindo permutação.
- Quatro originais confirmadas3/3: accommodates,availability_365,distance_to_geo_reference_km,cleaning_fee. Outras:longitude1confirmação+1tentativa,room_type1,bathrooms1. Confirmada/tentativa são contagens independentes por indicadores, não estados mutuamente exclusivos.
- Permutação3repetições ematé1.200linhas retidas/fold: maiores aumentos médios de MAPE13,4559p.p.(accommodates),6,8492(room_type),4,3212(distância),3,8730(disponibilidade),1,9302(longitude),1,3138(extra_people),0,9879(cleaning_fee); todos positivos3/3. Amostragem/orçamento fixos de diagnóstico; pequenas importâncias não justificam descarte automático.
- Validação270 com mesmo RF60árvores,profundidade12,folha5,seed42: conjunto36 MAPE29,7496%,MAE€44,2760,RMSE€177,2450,viés−€1,2361. Conjunto4 MAPE34,0499%,MAE€49,0328,RMSE€179,5376,viés−€1,4834. Redução de4,3003p.p. com36.
- Grupo com histórico(n2.659):MAPE28,1390%(36)vs33,0520%(4). Sem histórico(n344):42,1989%(36)vs41,7631%(4). Não alegar superioridade uniforme; o candidato completo vence globalmente, mas ainda tem maior erro no público sem histórico.
- Recomendação:manter36features para preparaçãoV2; não reduzir automaticamente ao núcleo Boruta. Não comparar esses números diretamente com LightGBM antigo de população diferente.
- Subagente revisou265–268 sem bug crítico no mapeamento/imputação/permutação. Limites de3folds/3repetições e confirmação por qualquer nível registrados. Fontes preservadas e teste com SHA-25612b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178.
- Nenhum tuning, exportação ou avaliação de teste nesta etapa. Gate05V2 aguarda usuário; Etapa06V2 não iniciada.
