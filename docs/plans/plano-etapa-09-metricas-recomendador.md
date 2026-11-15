# Etapa 09 — Métricas e Recomendador

**Status:** execução concluída; gate aprovado pelo usuário em 12/11/2026; Etapa 10 autorizada.

## Objetivo

O registro abaixo preserva a execução histórica. A reavaliação após a auditoria dos dados está em [Etapa 09 V2](plano-etapa-09-v2-metricas-recomendador.md), com população ampliada, 36 features e limitações de independência do teste documentadas.

Retreinar o LightGBM ajustado da Etapa 08 em treino + validação, avaliar uma vez no teste independente e produzir em memória preços de referência, diferenças para o preço anunciado e faixas empíricas de incerteza.

## Escopo e premissas

- Candidato congelado: `LightGBM ajustado`, com os parâmetros e as 40 features aprovadas na Etapa 08.
- Desenvolvimento final: 12.186 linhas de treino + 2.619 de validação = 14.805 anúncios. Semente 42.
- O teste original permanece em `data/processed/df_test_raw.csv`, com 3.005 linhas × 96 colunas como texto. Só será carregado depois de congelar modelo e calibração.
- Reconstruir no teste os dois agregados de `reviews.csv` até 06/12/2018 e as 22 features determinísticas da Etapa 03; reutilizar o centro geográfico calculado no treino.
- Limpar uma cópia do teste com as regras já decididas: bairros oficiais de Amsterdam, `price > 0`, remover `bathrooms >= 10`, remover o anúncio específico `id=7447773` se estiver com `maximum_nights=9999` e descartar casos incompletos nas features/alvo. Manter `bathrooms=0` e demais preços extremos.
- Criar uma faixa empírica central de 90% com os quantis 5% e 95% dos resíduos assinados out-of-fold em 5 folds no desenvolvimento. Medir a cobertura no teste sem ajustar a faixa com ele; não apresentar a faixa como garantia conformal formal.
- Não fazer novo tuning, seleção de features ou mudanças nas regras após observar resultados do teste. Não gravar modelo nem recomendações em arquivo.

## Estratégia

1. Verificar via MCP a aprovação da Etapa 08, o kernel, os parâmetros congelados, o pré-processador, as partições e o arquivo bruto do teste.
2. Concatenar treino e validação, calcular previsões out-of-fold com `KFold(n_splits=5, shuffle=True, random_state=42)` e pipeline completo. Obter os resíduos para a faixa empírica; depois ajustar o pipeline final em todo o desenvolvimento.
3. Carregar o teste bruto numa cópia, validar IDs/esquema/hash e aplicar parsing, limpeza, agregação de avaliações e engenharia de features já definidas, sem usar `price` para criar preditores.
4. Fazer uma previsão final no teste e calcular MAPE, MAE, RMSE, viés, cobertura/largura da faixa, métricas por tipo de quarto/faixa de preço e tabela de recomendação por `id`.
5. Auditar que o arquivo bruto não mudou, as previsões são finitas e o teste não foi usado em fit, tuning ou calibração.

## Células previstas

1. `## Etapa 09 — Métricas e Recomendador`: objetivo, candidato congelado, teste reservado e limites da interpretação.
2. `### 09.1 — Verificação e ajuste final`: versões/estado, composição treino + validação, previsões OOF de calibração e pipeline final.
3. `### 09.2 — Preparação da partição de teste`: leitura bruta, filtros aprovados, avaliações até o snapshot e reconstrução das 40 features.
4. `### 09.3 — Avaliação independente`: uma previsão final e métricas globais no teste.
5. `### 09.4 — Segmentos, incerteza e preços de referência`: desempenho por segmentos, cobertura da faixa e diferenças por anúncio, em memória.
6. `### 09.5 — Auditoria e gate`: integridade do teste, evidências, limitações e decisão.

Cada bloco será desenvolvido e executado via MCP em 1–3 células, com inspeção das saídas antes do próximo bloco. As células de código terão comentários em português; não serão definidas funções, classes ou lambdas.

## Critérios de aceite

- [x] O LightGBM usa exatamente os parâmetros congelados e todas as 40 features aprovadas.
- [x] O modelo final é ajustado em treino + validação; o pré-processamento aprende somente nesses dados.
- [x] A calibração usa apenas resíduos out-of-fold do desenvolvimento; sua interpretação e cobertura observada ficam documentadas.
- [x] O teste é limpo somente após congelar modelo e calibração; nenhuma previsão do teste participa do ajuste.
- [x] A limpeza registra contagens por regra e preserva o arquivo bruto original.
- [x] MAPE, MAE, RMSE, viés e métricas por segmento são calculados e reportados uma vez.
- [x] A recomendação traz `id`, preço anunciado, preço de referência, diferença em euros/percentual e faixa de incerteza; é indicada, não um preço ótimo comprovado.
- [x] Modelo e recomendações permanecem em memória, sem exportação.
- [x] O gate registra limitações e aprovação pendente antes da Etapa 10.

## Gate

**Estado:** aprovada pelo usuário em 12/11/2026; Etapa 10 autorizada.

## Evidências e decisões da execução

- O pipeline LightGBM aprovado foi ajustado em 14.805 anúncios de treino + validação, com 40 features e os parâmetros da Etapa 08. O esquema e os parâmetros finais foram conferidos.
- A calibração usou 5 folds no desenvolvimento: MAPE OOF agregado de 26,911%; resíduos `real - previsão` nos quantis 5% e 95% de −€74,1041 e +€81,6084.
- O teste bruto tinha 3.005 × 96. Após limpeza em cópia, 2.562 × 40 seguiram para avaliação. Saíram 4 linhas com `bathrooms` ausente e 439 com ausência em outras features/alvo. Não houve remoções por bairro, preço ausente/não positivo, `bathrooms >= 10`, `id=7447773` com `maximum_nights=9999` ou ausência de data de avaliação. `bathrooms=0` e os demais preços extremos foram preservados.
- Os eventos de `reviews.csv` tinham 0 datas inválidas e 0 eventos posteriores ao snapshot para os anúncios de teste; nenhum anúncio avaliado ficou sem data de última avaliação.
- Métricas no teste: MAPE 25,1276%; MAE €36,4427; RMSE €79,3473; viés previsão − real de −€0,3551. A avaliação ocorreu uma vez, depois de congelar modelo e calibração.
- Por tipo de quarto: casa/apartamento inteiro, `n=2.063`, MAPE 23,6664%; quarto privado, `n=494`, MAPE 30,4019%; quarto compartilhado, `n=5`, MAPE 106,9008%. O grupo compartilhado é pequeno para conclusões firmes.
- Por faixas definidas pelos quartis do desenvolvimento: Q1 `n=574`, MAPE 41,1951%; Q2 `n=725`, 19,0038%; Q3 `n=664`, 19,0081%; Q4 `n=599`, 23,9260% e RMSE €150,2714.
- A faixa empírica nominal de 90% teve cobertura observada de 90,20% e largura média de €155,32. É evidência desta amostra, sem garantia formal.
- Uma saída bruta do modelo foi negativa. Ela permanece nas métricas e é limitada a €0 somente no preço de referência da tabela, com indicador. `df_price_recommendations` tem 2.562 linhas e permanece em memória; não houve exportação.
- SHA-256 do teste antes e depois: `12b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178`; igual nos dois momentos.
- Limitação: a avaliação cobre casos completos após as regras de qualidade; não demonstra preço ótimo, causalidade ou receita incremental realizada.
- Após a aprovação da Etapa 09, o kernel perdeu as previsões e recomendações mantidas apenas em memória. Em 12/11/2026, o usuário autorizou executar novamente o notebook inteiro para recuperar esses objetos. A reprodução deve usar as células, features, parâmetros e regras aprovados, conferir as métricas salvas e proteger o arquivo bruto do teste pelo SHA-256 acima; não autoriza retuning nem mudança da avaliação aprovada.
