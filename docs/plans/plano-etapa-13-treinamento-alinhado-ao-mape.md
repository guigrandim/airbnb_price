# Etapa 13 — Treinamento alinhado ao MAPE

Em 20/11/2026, o usuário escolheu o objetivo alinhado ao MAPE e autorizou seguir. A Etapa 12 está aprovada. A Etapa 13 foi executada pelo MCP Jupyter e aguarda aprovação.

## Objetivo e desenho

Medir se treinar o LightGBM para reduzir erro relativo aproxima o modelo da meta de 10%. A variante usa perda absoluta com peso 1/preço em cada linha de treino. Para preços positivos, essa perda ponderada é proporcional ao MAPE no conjunto de ajuste. O peso entra apenas no treinamento. A avaliação calcula MAPE sem pesos adicionais.

A comparação usa as mesmas 36 variáveis, 17.021 observações, cinco folds com semente 42 e parâmetros estruturais da Etapa 12. Cada pré-processador é ajustado dentro do fold. O teste histórico fica fora do experimento. O baseline OOF deve reconciliar com 27,172418%. A análise usa o snapshot de dezembro de 2018.

## Blocos previstos

1. **13.1 — Verificação do contrato OOF.** Confirmar via MCP o kernel, as versões, o alinhamento de IDs e preços, a positividade dos alvos e a referência da Etapa 12. Se necessário, reconstruir os objetos executando apenas as células pertinentes da Etapa 12.
2. **13.2 — Verificação do treinamento ponderado.** Ajustar cinco pipelines com perda absoluta e pesos inversos ao preço do treino. Conferir pesos finitos e positivos e cobertura de uma previsão retida por anúncio.
3. **13.3 — Verificação do desempenho.** Comparar MAPE, MAE, RMSE e viés na população completa e nos mesmos folds. Detalhar os cortes de €95, €125 e €175, a cauda do erro e a contagem de previsões não positivas.
4. **13.4 — Verificação final.** Registrar a distância até 10%, as diferenças por faixa e o status do gate no notebook e neste plano.

## Critérios de aceite

- Comparar ambos os modelos nos mesmos IDs retidos e verificar que todos os anúncios de desenvolvimento receberam uma previsão.
- Considerar a variante promissora se reduzir o MAPE global e em pelo menos quatro folds. Relatar qualquer aumento de MAE, RMSE ou viés por faixa antes de propor adoção.
- Registrar a meta como atingida neste diagnóstico somente se o MAPE global for de até 10%. A análise OOF no desenvolvimento serve como evidência interna.
- Executar e inspecionar os blocos pelo MCP Jupyter e preservar os resultados aprovados.

## Evidências e decisão

- Após reiniciar a sessão, o MCP voltou a responder. A referência foi reconstruída em memória com Python 3.13.17, scikit-learn 1.7.2 e LightGBM 4.7.0. O baseline reproduziu 27,172418% de MAPE.
- Os 17.021 IDs receberam uma previsão retida por modelo. Nenhuma previsão foi não positiva. O holdout histórico ficou fora da avaliação.
- MAPE global de 27,172% para 22,432%, com melhora em cinco folds e distância de 12,432 pontos percentuais até a meta. P95 do erro percentual absoluto de 78,497% para 55,999%.
- MAPE por faixa de 44,149% para 26,177% até €95, de 21,818% para 14,813% entre €95 e €125, de 18,961% para 17,882% entre €125 e €175 e de 23,615% para 31,342% acima de €175.
- MAE global de €39,602 para €41,140 e RMSE de €128,671 para €136,807. O viés acima de €175 passou de −€50,432 para −€105,444.
- A variante atingiu o critério de melhora do MAPE. A piora nos preços altos e nas métricas em euros sustenta manter o V2 como referência. O notebook foi salvo e conferido pelo MCP.
