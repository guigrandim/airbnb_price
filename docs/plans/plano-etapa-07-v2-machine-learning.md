# Etapa 07 V2 — Machine Learning

Data 15/11/2026. Etapa07V2 aprovada pelo usuário. Etapa08V2 autorizada com XGBoost eLightGBM.

## Objetivo

Comparar modelos sobre as36features aprovadas e escolher candidatos para tuning com base na validação de3.003anúncios.

## Estratégia e premissas

- Treino14.018linhas e validação3.003linhas. Confirmar kernel, dados, exclusão ID20644162, templates e versões. Toda preparação é ajustada no treino de cada pipeline.
- DummyRegressor média como baseline e mediana como diagnóstico.
- LinearRegression com preparação robusta. Polinomial grau2 apenas entre23contínuas, com binárias, indicadores de ausência e one-hot aditivos. Limite esperado406colunas antes do estimador.
- RandomForest300árvores,profundidade12,folha5,seed42. XGBoost300árvores,profundidade6,learning_rate0,05,subsample0,8,colsample_bytree0,8,seed42. LightGBM300iterações,31folhas,learning_rate0,05,subsample0,8,subsample_freq1,colsample_bytree0,8,seed42.
- Configurações fixas de comparação. Fit no treino e métricas calculadas sobre previsões brutas de treino/validação, incluindo eventual previsão não positiva.
- Reportar MAPE principal, MAE,RMSE,viés,tempo e p95/p99 do erro. Segmentos por room_type,histórico e quartis com cortes definidos no treino.
- Diagnóstico de diferenças entre partições com distribuição do alvo, deslocamentos de features e erros por faixa. Nenhuma linha removida por erro do modelo.
- Teste consultado apenas pelo hash, dados/modelos em memória. Ranking usado para recomendar finalistas à Etapa08V2.

## Células previstas

1. Contrato, dependências e preparação de objetos de métricas.
2. Baselines e inspeção.
3. Regressões linear/polinomial e inspeção.
4. Árvores/boosting e inspeção.
5. Ranking, caudas, segmentos e diagnóstico treino–validação.
6. Auditoria, interpretação e gate.

## Critérios de aceite

- Sete estimadores com as mesmas partições,36entradas e fit de transformadores no treino.
- Métricas finitas e população reconciliada, tempos e parâmetros registrados.
- Polinomial controlada e previsões não positivas identificadas.
- Fontes e teste íntegros, evidências salvas via MCP.
- Gate07V2 solicitado antes da Etapa08V2.

## Evidências e gate

- Entrada verificada no kernel ativo. pandas2.3.3,numpy2.2.6,sklearn1.7.2,XGBoost3.2.0,LightGBM4.7.0.
- Baselines executados. MAPE validação49,0418% para média e38,2209% para mediana.
- Regressões executadas com130e406colunas. MAPE validação31,9074% linear e33,4391% polinomial. Oito e12previsões não positivas na validação. Ajustes0,66s e4,67s.
- Árvores concluídas. RandomForest60,76s,XGBoost5,02s,LightGBM2,12s. Total de ajuste dos sete estimadores73,63s.
- Ranking de MAPE validação com3.003anúncios

| Modelo | MAPE (%) | MAE (€) | RMSE (€) | Viés (€) |
|---|---:|---:|---:|---:|
| XGBoost |29,1213|43,3946|178,9912|−0,1045|
| LightGBM |29,4266|43,9089|174,5383|−1,4377|
| Random Forest |29,8071|44,1594|177,1998|−0,9995|
| Linear |31,9074|46,2645|178,9078|−1,4192|
| Polinomial |33,4391|47,7279|182,7256|−0,4640|
| Dummy mediana |38,2209|59,4199|193,4658|−27,1175|
| Dummy média |49,0418|63,0130|191,5563|−0,4102|

- XGBoost teve MAPE treino20,6926%,gap8,4287p.p. LightGBM23,7714%,gap5,6552p.p. RF23,9156%,gap5,8915p.p. Comparação aponta erro maior fora do ajuste, especialmente nos grupos sem histórico e preços baixos.
- Históricos n2.659 tiveram MAPE27,2012%XGB/27,3647%LGB. Sem histórico n344 tiveram43,9628%/45,3643%. Quartos compartilhados n9 na validação limitam interpretação do segmento.
- Quartis do treino em€95/€125/€175. Q1 MAPE46,0977%XGB/45,9537%LGB,com viés+€27,63/+€26,63. Q4 MAPE24,3326%/24,3727%,MAE€87,12e viés−€55,08/−€57,45.
- APE p99 validação179,0771%XGB/173,0271%LGB. LightGBM produziu uma previsão não positiva na validação, além das8lineares e12polinomiais. Previsões brutas mantidas nas métricas.
- Distribuição do alvo KS D0,01731,p0,44438. Maior SMD numérico0,0363 e maior variação total categórica2,6203%em bairro. Médias€151,707/€152,118,medianas€125/€129,desvios€137,613/€191,588. A semelhança central coexiste com caudas raras diferentes.
- Maiores resíduos absolutos incluem anúncio258273,preço€8.000,previsão€178,99XGB/€216,81LGB;5587500,€4.500;11040717,€2.500. São diagnósticos de validação e não regras novas de exclusão.
- A primeira reconciliação de segmentos teve erro de alinhamento de nomes do índice pandas. Corrigida para contagem por modelo/partição, a célula294 foi reexecutada com as mesmas previsões. Ajustes de modelos não foram repetidos para essa correção.
- Auditoria final296 válida com7modelos,14linhas de métricas,119.147linhas de diagnóstico,36entradas,previsões finitas e fonte preservada. Hash teste conferido sem avaliação.
- Recomendação de finalistas para08V2 ficou XGBoost eLightGBM. São referências de parâmetros fixos para o tuning posterior. A integraçãoV2 não representa reprodução das métricas históricas de população menor.

## Gate

Revisão estática independente das células285–296 concluída pelo subagente sem bugs concretos. Conferidos fit no treino, alinhamento das previsões, expansão polinomial somente em contínuas, métricas brutas, quartis do treino e reconciliação de segmentos.

Etapa07V2 executada, aguardando aprovação para08V2. Etapa06V2 é a última etapa aprovada da revisão. Teste e dados brutos preservados, modelos e previsões em memória.
