# Etapa 07 — Machine Learning

**Status:** execução concluída; gate aprovado pelo usuário em 10/11/2026. A Etapa 08 está autorizada.

## Objetivo

Treinar e comparar modelos de regressão para estimar o preço em Amsterdam, escolhendo candidatos para tuning sem consultar o conjunto de teste.

## Escopo e premissas

- Usar as 40 features aprovadas na Etapa 05 e os pipelines preparados na Etapa 06.
- Treino: selection_train (12.186 linhas); validação: selection_validation (2.619 linhas). Confirmar dimensões no kernel antes de ajustar.
- Alvo price positivo; métricas calculadas em euros e MAPE em percentual.
- Treinar somente no treino e comparar uma vez na validação. Não carregar df_test_raw.csv, não ajustar hiperparâmetros e não salvar previsões ou modelos em disco.
- Manter os dados de origem e df_modeling_features inalterados.
- Usar seed 42 e configuração fixa, com orçamento comparável. O ranking de validação é triagem para tuning, não resultado final.

## Estratégia

1. Confirmar o estado do kernel/MCP, a integridade das partições, features, alvo, pipelines e disponibilidade das bibliotecas. Reutilizar stage06_scaled_pipeline para regressões sensíveis à escala e stage06_tree_pipeline para árvores.
2. Construir baselines DummyRegressor(strategy="mean") e DummyRegressor(strategy="median"); a mediana fica como diagnóstico, não como baseline principal.
3. Ajustar LinearRegression e regressão polinomial de grau 2. Na polinomial, criar interações somente entre as 24 numéricas contínuas; manter os 9 indicadores binários e as categóricas one-hot como efeitos aditivos. Reutilizar os transformadores da Etapa 06 e manter a saída esparsa para controlar complexidade e memória.
4. Ajustar RandomForestRegressor (300 árvores, profundidade 12, folha mínima 5, random_state=42) e modelos XGBoost/LightGBM com 300 árvores/iterações, learning rate 0,05, subsampling 0,8 e seed 42. Registrar configurações e tempo. Se uma dependência não estiver disponível no kernel do notebook, interromper esse comparativo e resolver a dependência local antes de declarar a etapa concluída.
5. Para cada modelo, registrar métricas no treino e na validação: MAPE, MAE, RMSE e viés médio (preço previsto menos preço observado). Reportar também métricas por room_type e quantis do erro percentual absoluto na validação para examinar caudas.
6. Antes do gate, investigar a diferença treino–validação: comparar a distribuição do alvo e das 40 features entre partições e calcular métricas de erro por faixas de preço comuns, com cortes definidos somente no treino. O teste continua intocado.
7. Comparar candidatos pela validação, registrar sobreajuste, tempo, erros por segmento e limitações. Recomendar os modelos para a Etapa 08 sem consultar o teste.
8. Executar verificação final do contrato, de ausência de vazamento e de integridade das fontes; registrar versões e o gate da Etapa 07.

## Células previstas

1. ## Etapa 07 — Machine Learning: objetivo, limites e separação do teste.
2. ### 07.1 — Verificação de entrada e dependências: kernel, partições, alvo, features, pipelines e pacotes.
3. ### 07.2 — Baselines: média e mediana.
4. ### 07.3 — Regressões lineares: linear e polinomial controlada.
5. ### 07.4 — Modelos de árvore e boosting: Random Forest, XGBoost e LightGBM.
6. ### 07.5 — Métricas e diagnóstico: MAPE/MAE/RMSE/viés, desempenho por room_type, caudas, tempo e sobreajuste.
7. ### 07.5.3 — Diferença treino–validação: distribuição do alvo/features e erro por faixa de preço com cortes do treino.
8. ### 07.6 — Ranking e gate: recomendação para tuning, versões, limites, integridade e aprovação.

Cada bloco de código terá comentários em português. Inserirei no máximo 1–3 células por bloco, executarei via MCP e inspecionarei as saídas antes de continuar.

## Critérios de aceite

- [x] MCP permite ler, inserir e executar as células do notebook; saídas são inspecionadas.
- [x] Os dois baselines e todos os modelos previstos usam exatamente as mesmas partições e 40 features.
- [x] Pré-processamento é ajustado apenas no treino; validação recebe somente predict/transform; teste não é lido.
- [x] MAPE, MAE, RMSE e viés são reportados para treino/validação e por room_type; erros de cauda e tempos são documentados.
- [x] Valores de price usados nas métricas são positivos, e o cálculo de MAPE não contém denominador inválido.
- [x] Dados de origem permanecem inalterados; nenhum modelo ou previsão é gravado em disco.
- [x] Ranking, candidatos à Etapa 08, versões, ressalvas e status do gate ficam registrados no notebook e neste plano.
- [x] Diagnóstico treino–validação compara alvo e features e mostra métricas por faixas de preço comuns, sem consultar o teste ou alterar os dados.

## Dependências

- Base: pandas 2.3.3, NumPy 2.2.6 e scikit-learn 1.7.2, conforme Etapa 06.
- Confirmar versões/disponibilidade de XGBoost e LightGBM no kernel ativo. Se ausentes, usar apenas dependências locais do projeto e validar o kernel após eventual instalação.

## Evidências e decisões

- A leitura MCP confirmou que o notebook termina na Etapa 06, com stage06_final_gate_valid=True salvo; 40 features, 12.186 linhas de treino, 2.619 de validação e 202 colunas transformadas.
- O arquivo de teste só foi inspecionado por existência e tamanho (11.634.013 bytes) na Etapa 06; permanece fora desta etapa.
- O kernel ativo é a .venv do projeto. XGBoost 3.2.0 e LightGBM 4.7.0 foram instalados localmente e registrados em requirements.txt; versões serão reconfirmadas pelo kernel.
- A primeira execução de 07.1 encontrou somente uma referência incorreta na linha de exibição. A célula foi corrigida via MCP; a execução seguinte passou com entrada válida e fontes intactas.
- Foram ajustados dois baselines e cinco modelos com seed 42: DummyRegressor de média/mediana; regressão linear; regressão polinomial grau 2 com interações apenas entre 24 contínuas; Random Forest (300 árvores, profundidade 12, folha mínima 5); XGBoost (300 árvores, profundidade 6, learning rate 0,05, subsampling 0,8); LightGBM (300 iterações, 31 folhas, learning rate 0,05, subsampling 0,8).
- Regressão linear: 202 colunas transformadas, 2,14 s de ajuste. Regressão polinomial: 478 colunas, 8,37 s. Random Forest: 47,35 s. XGBoost: 6,48 s. LightGBM: 2,49 s. O ajuste total dos sete estimadores foi 66,84 s.
- Na validação, o ranking por MAPE foi LightGBM 27,363% (MAE €41,849; RMSE €180,627; viés −€3,333), XGBoost 27,367% (€42,007; €185,879; −€2,074), regressão linear 28,252% (€42,691; €184,612; −€3,222), Random Forest 28,575% (€43,062; €183,317; −€1,987), polinomial 30,095% (€44,709; €184,720; −€1,916), baseline mediana 37,190% (€57,048; €196,920; −€24,904) e baseline média 46,128% (€59,876; €195,349; −€2,008).
- Foram recomendados LightGBM e XGBoost para a Etapa 08. O LightGBM teve MAE/RMSE globais menores; XGBoost teve p95 de erro percentual absoluto menor (70,27% versus 74,00%). Por segmento, XGBoost teve menor MAPE em Entire home/apt (n=2.045) e LightGBM em Private room (n=566); Shared room teve apenas 8 linhas e não suporta conclusão estável.
- Os cortes de preço definidos no treino foram €95, €125 e €175. O MAPE dos modelos explicativos foi 39%–44% no primeiro quartil; no quarto, 21%–25%, com MAE €83–€88 e viés negativo. O p99 de erro percentual absoluto excedeu 140% nos dois finalistas. Regressão linear e polinomial geraram 3 e 6 previsões não positivas na validação; não houve clipping ou exclusões adicionais.
- A verificação final passou: 14 linhas de métricas globais, cobertura de 2.619 linhas por room_type e por faixa, previsões finitas, 40 features de entrada e df_modeling_features inalterado. O teste foi consultado apenas por existência/tamanho; nenhum modelo ou previsão foi salvo em disco.
- Diagnóstico complementar executado antes do gate: o preço tem mediana €125 em ambas as partições, médias €147,90/€149,90 e KS D=0,0162 (p=0,6137). O maior SMD numérico foi 0,046; a maior distância de variação total categórica foi 4,52%; categorias inéditas na validação cobrem no máximo 0,23% das linhas. O gap de MAPE dos modelos de árvore persistiu nos quatro quartis comuns. O p99 do APE aumentou 33,22 p.p. no LightGBM, 45,08 p.p. na Random Forest e 58,03 p.p. no XGBoost, contra 3,55 p.p. na regressão linear e 9,51 p.p. na polinomial. A faixa mais cara manteve viés de subestimação; nenhum dado foi alterado.
- O usuário aprovou a Etapa 07 para avançar à Etapa 08 em 10/11/2026. O teste permanece reservado para a avaliação única da Etapa 09.

## Gate

**Estado:** aprovado pelo usuário em 10/11/2026; Etapa 08 autorizada.

Decisão registrada: **“Aprovo, pode seguir”** (10/11/2026).

## Diagnóstico complementar antes do gate

**Objetivo:** verificar se a diferença de MAPE entre treino e validação decorre de distribuições diferentes entre partições, de uma faixa de preço específica ou de generalização mais fraca.

**Escopo e estratégia:** análise somente de `stage07_X_train`, `stage07_X_validation`, `stage07_y_train`, `stage07_y_validation` e previsões já produzidas. Comparar estatísticas do alvo, KS como medida descritiva, deslocamento padronizado das features numéricas e distância de variação total das categóricas. Calcular MAPE, MAE e viés por quartis comuns, usando os cortes já definidos pelo treino, e comparar p95/p99 do erro percentual absoluto entre partições. Não limpar dados, retreinar modelos, consultar teste ou alterar features.

**Células previstas:** inserir `### 07.5.3 — Diferença treino–validação` com uma célula Markdown de contexto, células Python comentadas para distribuição/erros por faixa e percentis da cauda, e uma interpretação Markdown baseada nas saídas.

**Critérios de aceite:** as duas partições são comparadas sem usar o teste; os cortes vêm só do treino; a tabela de erros mostra ambos os conjuntos por faixa e nos percentis p95/p99; as maiores diferenças de distribuição são listadas e interpretadas com cautela; nenhuma linha ou feature é alterada.

**Status:** diagnóstico executado via MCP; distribuição do alvo/features, erros por faixa, percentis p95/p99 e gate final inspecionados. O gate da Etapa 07 foi aprovado pelo usuário em 10/11/2026.
