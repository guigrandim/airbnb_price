# Etapa 05 — Seleção de Features

**Status:** reconstruída e conferida após restart em 09/11/2026; avanço para a Etapa 06 autorizado pelo usuário.

## Objetivo

Identificar um subconjunto estável das preditoras de preço e verificar se ele melhora ou preserva o MAPE na validação.

## Escopo e base

- Fonte: `df_modeling_features`, atualmente com 14.805 linhas e 45 colunas: 12.186 de treino e 2.619 de validação.
- Candidatas registradas: 42 (34 numéricas, 7 categóricas e a data `host_since`). A data bruta é redundante com `host_tenure_years`, criada na Etapa 03; a matriz efetiva usará as 41 features restantes (34 numéricas, incluindo tempo de anfitrião, e 7 categóricas).
- Excluir `id`, `price`, `particao` e `host_since` bruto da matriz. `price` permanece apenas como alvo; `host_since` não perde informação porque `host_tenure_years` deriva dela pela data fixa do snapshot.
- Usar `particao == "treino"` para seleção; usar validação somente para a comparação final dos dois conjuntos de features. Não ler o teste.
- Não modificar `df_modeling_features`, `df_modeling_final`, dados brutos ou `df_test`.

## Estratégia

1. Confirmar nomes, tipos e contagens das partições, preço positivo e as 42 candidatas registradas no kernel ativo.
2. Verificar que `host_tenure_years` corresponde a `(2018-12-06 - host_since).dt.days / 365.25`; usar apenas a feature numérica já criada na Etapa 03 para evitar duplicar o mesmo sinal.
3. Em 5 folds de `KFold` no treino (`shuffle=True`, `random_state=42`), ajustar imputação e `OneHotEncoder(handle_unknown="ignore", sparse_output=False`) somente nos dados de treino de cada fold. Aplicar BorutaPy (`max_iter=30`) com `RandomForestRegressor` determinístico (80 árvores, profundidade máxima 12, folha mínima 5, seed por fold) às 41 features efetivas. Não usar validação para seleção.
4. Agregar os níveis one-hot de cada variável categórica à feature original. Relatar seleção confirmada, tentativa e frequência entre folds. Definir como estáveis as features confirmadas em pelo menos 3 dos 5 folds; não selecionar pela validação.
5. Revisar redundância nos conjuntos usando somente treino. Se `accommodates_log1p` corresponder exatamente a `accommodates`, removê-la dos dois candidatos para manter a comparação justa; conservar a escala original por interpretabilidade e adequação às árvores. Registrar ambas na tabela Boruta e a remoção da transformação derivada.
6. Ajustar, no treino completo, a mesma configuração fixa de `RandomForestRegressor` para dois candidatos: todas as 40 features únicas restantes e o conjunto estável sem redundâncias. Aplicar somente `transform` à validação e comparar MAPE, MAE, RMSE e viés. Não fazer tuning nesta etapa.
7. Registrar o conjunto recomendado, sua estabilidade, métricas e ressalvas. Se Boruta não confirmar features estáveis ou se o conjunto ficar vazio, registrar a limitação e não inventar um subconjunto.

## Complemento implementado — Importância por permutação out-of-fold

### Objetivo e escopo

Verificar se cada uma das 40 features únicas contribui para a previsão da Random Forest quando avaliada em linhas que ficaram fora do ajuste. As categóricas serão permutadas como colunas originais completas, e os resultados serão agregados por feature entre cinco folds internos do treino.

### Estratégia e premissas

1. Usar `KFold(n_splits=5, shuffle=True, random_state=42)` nas 12.186 linhas de treino; não usar a validação nem o teste.
2. Em cada fold, ajustar imputadores, `OneHotEncoder` e `RandomForestRegressor` somente na parte de ajuste. Usar o mesmo modelo de triagem da comparação anterior (`n_estimators=300`, `max_depth=12`, `min_samples_leaf=5`), com seed fixa por fold.
3. Calcular importância por permutação na parte retida do fold, passando o DataFrame original à pipeline. Assim cada variável categórica é embaralhada inteira, sem separar os indicadores one-hot.
4. Usar 10 permutações por feature e registrar aumento de MAPE em pontos percentuais e aumento de MAE em euros; resumir média, desvio-padrão e sinal por fold.
5. Tratar a saída como diagnóstico de contribuição para esta Random Forest, não como teste causal nem como novo corte de seleção. Features correlacionadas podem mascarar importância individual; interpretar junto à análise de redundância.

### Células e critérios de aceite

- Inserir a subseção `### 05.4.1 — Importância por permutação out-of-fold` e a leitura em `### 05.4.2`, com explicação antes do código e interpretação depois da saída.
- O código deve ajustar toda transformação somente no fold de ajuste, permutar somente o fold retido, confirmar dimensões/valores finitos e manter `df_test` fora do fluxo.
- Apresentar tabela por feature com média e dispersão das mudanças em MAPE/MAE e número de folds com importância positiva.
- Registrar seed, configuração, número de permutações e limite de interpretação; manter a recomendação anterior de 40 features até avaliação comparativa própria.
- A execução não deve depender de objetos de Boruta em memória, para evitar reexecutar essa seleção após o kernel reiniciado.

**Status do complemento:** permutação OOF e Boruta repetidos após o restart via MCP Jupyter em 09/11/2026; verificações finais passaram e os resultados reproduziram o registro.

## Premissas

- Os preços de treino e validação são positivos, condição necessária ao MAPE; confirmar essa condição antes de calcular métricas.
- `host_tenure_years` usa a referência fixa de 06/12/2018 documentada na Etapa 03. Imputadores e encoder são ajustados dentro de cada fold e depois somente no treino completo.
- A lista de 42 candidatas da EDA inclui a data bruta e sua derivada numérica; a matriz remove `host_since` após conferir equivalência, evitando avaliar duas representações do mesmo dado.
- Features one-hot selecionadas serão agregadas ao atributo categórico de origem; não serão expostas como nomes independentes na seleção final.
- O modelo de comparação é um estimador de triagem com seed e hiperparâmetros fixos, não o ranking de modelos da Etapa 07.
- A validação não define quais features entram no conjunto estável; serve apenas para comparar os dois conjuntos após a seleção e a revisão de redundância no treino.

## Células previstas no notebook

1. `### 05.1 — Verificação dos dados e candidatos`: partições, alvo, colunas proibidas, tipos, contagem das 42 candidatas e equivalência da data derivada.
2. `### 05.2 — Boruta e estabilidade no treino`: folds, pré-processamento ajustado por fold, seleção Boruta e frequência agrupada por feature original.
3. `### 05.3 — Revisão do conjunto selecionado`: tabela de ranking/estado/frequência, redundâncias e definição do conjunto estável.
4. `### 05.4 — Comparação na validação`: pipelines fixos para as 40 features únicas e para as estáveis; MAPE, MAE, RMSE e viés.
5. `### 05.4.1 — Importância por permutação out-of-fold`: análise complementar em cinco folds internos do treino.
6. `### 05.4.2 — Interpretação do double check`: resultados e limites da permutação comparados conceitualmente a Boruta.
7. `### 05.5 — Verificação final e gate`: checagens antileakage, resumo, limitações e aprovação para a Etapa 06.

## Dependências previstas

- `scikit-learn==1.7.2`, compatível com o Python 3.10 do projeto.
- `Boruta==0.4.3`, módulo `boruta.BorutaPy`.
- Instalação restrita ao `.venv` do projeto; versões registradas em `requirements.txt`.

## Critérios de aceite

- [x] Kernel e `.venv` local carregam scikit-learn 1.7.2 e Boruta 0.4.3, com versões registradas em `requirements.txt`.
- [x] Matriz de seleção contém as 41 features efetivas; `id`, `price`, `particao` e `host_since` bruto não entram como preditoras.
- [x] Boruta e pré-processadores foram ajustados somente em folds do treino; o teste não foi consultado.
- [x] Estabilidade e agrupamento das categorias one-hot por feature original estão documentados.
- [x] As 40 features únicas e o subconjunto estável de uma feature foram comparados na validação com a mesma configuração e MAPE, MAE, RMSE e viés.
- [x] A importância por permutação OOF cobriu 40 features nos cinco folds internos, com pré-processamento ajustado só no fold de treino; validação e teste ficaram fora desta análise.
- [x] Tabela e interpretação registram MAPE/MAE, dispersão entre folds, sinais positivos, configuração fixa e limites de leitura.
- [x] A cópia do treino confere com a referência da Etapa 04; partições e fontes não foram alteradas.
- [x] Notebook registra resultados, ressalvas e o gate da Etapa 05.

## Evidências e resultado da execução

- O kernel e a `.venv` carregam `scikit-learn==1.7.2` e `Boruta==0.4.3`; imports executados com sucesso e dependências fixadas em `requirements.txt`.
- A base de modelagem permaneceu com 14.805 linhas: 12.186 treino e 2.619 validação. A matriz não inclui `id`, `price`, `particao` ou o teste.
- As 42 candidatas de origem se tornam 41 atributos efetivos ao manter `host_tenure_years` e excluir `host_since`; equivalência confirmada no treino com diferença máxima de 0 anos.
- Boruta rodou em cinco folds, com imputação e one-hot ajustados dentro do treino de cada fold. Confirmou `accommodates` e `accommodates_log1p` em 5/5 folds. O critério de estabilidade também exige 3/5; as duas atingiram 5/5.
- A distribuição entre as 41 features efetivas foi: 2 confirmadas em 5/5, nenhuma em 3–4/5, 9 confirmadas em 1–2/5, 1 apenas tentada ao menos uma vez e 29 sem confirmação nem tentativa. Portanto, 2/41 (4,9%) atingiram o corte de estabilidade; ambas representam o mesmo sinal de capacidade, pois `accommodates_log1p` é exatamente `log1p(accommodates)`. Após deduplicar, há um único sinal estável distinto.
- `availability_365` e `distance_to_training_center_km` tiveram confirmação em 2/5 folds e tentativa nos outros 3; `host_tenure_years` foi confirmada em 2/5 e tentada em 1/5. A frequência de uma categórica conta como confirmada quando ao menos um indicador one-hot foi confirmado; os totais por fold referem-se a indicadores, não a features originais.
- A leitura de estabilidade usa uma única validação cruzada de cinco folds com seed 42. Não mede variação entre seeds ou configurações de Boruta e não garante estabilidade geral.
- A equivalência `accommodates_log1p == log1p(accommodates)` foi confirmada no treino. A transformação foi removida dos dois conjuntos de comparação; o conjunto completo ficou com 40 features únicas e o estável com `accommodates`.
- Na validação, com `RandomForestRegressor` fixo (300 árvores, profundidade 12, folha mínima 5, seed 42):
  - 40 features: MAPE 28,5766%, MAE €43,0556, RMSE €183,2673, viés −€1,9848.
  - `accommodates`: MAPE 36,0176%, MAE €50,8573, RMSE €188,6463, viés −€3,3202.
- Recomenda-se manter as 40 features únicas para a Etapa 06: o subconjunto de um único sinal teve MAPE de 36,02%, contra 28,58% com as 40. O resultado vem de um único estimador de triagem e de uma validação; não é a avaliação final do modelo. O conjunto de teste não foi consultado.
- A permutação OOF usou 12.186 linhas de treino, KFold com 5 partes (`shuffle=True`, seed 42), 40 features originais (33 numéricas e 7 categóricas), 10 permutações por feature e `RandomForestRegressor` com 300 árvores, profundidade 12, folha mínima 5 e seed 42. A pipeline ajustou imputadores e one-hot em cada fold de ajuste.
- As previsões OOF tiveram MAPE agregado de 27,73% e MAE de €39,22. As quatro maiores importâncias médias foram `accommodates` (+12,054 p.p.), `room_type` (+6,923 p.p.), `distance_to_training_center_km` (+6,246 p.p.) e `availability_365` (+4,227 p.p.); cada uma teve ΔMAPE e ΔMAE positivos em 5/5 folds.
- 38 das 40 features tiveram ΔMAPE médio positivo; muitas das menores diferenças ficaram próximas de zero. O diagnóstico apoia manter o conjunto de 40 como referência, mas não define um novo corte e não transforma uma associação preditiva em efeito causal.
- A permutação e Boruta são evidências complementares, com critérios diferentes. Features correlacionadas podem repartir importância. A tabela completa de média, dispersão e sinal por fold está na subseção 05.4.1 do notebook.
- Após o reinício do kernel, a verificação atual da análise OOF passou. Boruta e comparação de validação não foram reexecutados; seus resultados anteriores permanecem registrados nas células salvas do notebook. A validação final tentou depender de `df_test` em memória; o teste não foi carregado para satisfazer essa dependência.
- Durante a reconstrução do kernel, a célula de verificação `03.6.3` falhou com `NameError` porque `df_test` não estava carregado. O holdout foi mantido fora da análise; essa verificação antiga precisará ser adaptada antes de uma execução linear completa do notebook.

## Pendências e gate

- Aprovação explícita da Etapa 05 antes de iniciar a Etapa 06.
- Adaptar a verificação final da Etapa 03 para não depender de `df_test` em memória quando o notebook for reexecutado desde o início.
- **Última etapa aprovada:** Etapa 04.
- Perguntar literalmente: **“Você aprova a Etapa 05 para avançarmos à Etapa 06?”**

## Referências técnicas

- [Instalação oficial do scikit-learn 1.7](https://scikit-learn.org/1.7/install.html)
- [BorutaPy — documentação e instalação](https://github.com/scikit-learn-contrib/boruta_py)

**Gate:** resultados reconstruídos e conferidos; o usuário autorizou avançar à Etapa 06 após a revisão.

**Notebook:** `notebooks/price_prediction.ipynb`.

## Reconstrução e conferência após restart

- O kernel reiniciou com execution_count=1. As células de preparação e seleção foram reexecutadas via MCP; o holdout foi mantido fora de Boruta, comparação na validação e permutação OOF.
- Boruta repetiu as confirmações por fold (2, 11, 2, 2 e 5); as únicas features estáveis em 5/5 foram accommodates e accommodates_log1p, sendo a segunda removida por redundância.
- A comparação na validação repetiu os resultados: 40 features com MAPE 28,58%/MAE €43,06; accommodates isolada com MAPE 36,02%/MAE €50,86.
- A permutação OOF repetiu MAPE 27,73%, MAE €39,22 e as quatro maiores importâncias: accommodates, room_type, distance_to_training_center_km e availability_365.
- A célula de verificação final da permutação passou; nenhuma métrica ou seleção usou o teste.
- O usuário autorizou o avanço à Etapa 06 após a reconstrução do kernel e revisão dos resultados.
