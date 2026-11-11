# Etapa 08 — Fine Tuning

**Status:** execução concluída e aprovada pelo usuário em 10/11/2026; Etapa 09 autorizada.

## Objetivo

Ajustar LightGBM e XGBoost, os dois candidatos aprovados na Etapa 07, com busca bayesiana via Optuna e comparar o resultado com as configurações fixas já avaliadas.

## Escopo e premissas

- Usar as 40 features aprovadas e os 12.186 registros de treino; manter os 2.619 registros de validação como holdout final da etapa.
- Otimizar MAPE em validação cruzada de 3 folds no treino, com `KFold(shuffle=True, random_state=42)`.
- Usar TPE com seed 42 e 20 trials por algoritmo. Trials são sequenciais; `cross_val_score` não paraleliza os folds.
- Montar cada estimador dentro do pipeline com `stage06_tree_preprocessor`; imputação e codificação serão ajustadas dentro de cada fold.
- Comparar cada busca com a configuração fixa da Etapa 07 sob os mesmos folds e com a validação holdout.
- Não carregar o teste, não alterar features aprovadas, não usar a validação no objetivo do Optuna e não salvar modelos ou previsões em disco.
- Não definir funções, classes ou lambdas no notebook; usar o fluxo `study.ask()` / `study.tell()` em loops sequenciais.
- Se Optuna não estiver disponível no kernel, instalar apenas no ambiente local do projeto, fixar a versão observada em `requirements.txt` e registrar a versão.

## Estratégia de busca

### LightGBM

- `n_estimators`: inteiro de 150 a 600.
- `learning_rate`: real de 0,01 a 0,10 em escala logarítmica.
- `max_depth`: inteiro de 4 a 12.
- `num_leaves`: inteiro de 15 a `min(63, 2**max_depth)` para respeitar a profundidade amostrada.
- `min_child_samples`: inteiro de 10 a 60.
- `subsample` e `colsample_bytree`: reais de 0,60 a 1,00; manter `subsample_freq=1`.
- `reg_alpha` e `reg_lambda`: reais de 0,001 a 10 em escala logarítmica.

### XGBoost

- `n_estimators`: inteiro de 150 a 600.
- `learning_rate`: real de 0,01 a 0,10 em escala logarítmica.
- `max_depth`: inteiro de 3 a 10.
- `min_child_weight`: real de 1 a 10 em escala logarítmica.
- `subsample` e `colsample_bytree`: reais de 0,60 a 1,00.
- `gamma`: real de 0 a 5.
- `reg_alpha` e `reg_lambda`: reais de 0,001 a 10 em escala logarítmica.

## Células previstas

1. `## Etapa 08 — Fine Tuning`: objetivo, limites, partições e candidatos.
2. `### 08.1 — Verificação de entrada e Optuna`: kernel, pacotes, partições, features, alvo e estado aprovado da Etapa 07.
3. `### 08.2 — Validação cruzada e referências`: definir folds, scorer MAPE, comparar configuração fixa dos dois modelos e confirmar escopo sem teste.
4. `### 08.3 — Busca Optuna para LightGBM`: 20 trials TPE, CV, parâmetros, tempo e melhor resultado.
5. `### 08.4 — Busca Optuna para XGBoost`: 20 trials TPE, CV, parâmetros, tempo e melhor resultado.
6. `### 08.5 — Comparação holdout`: refazer cada pipeline vencedor no treino completo e avaliar uma vez na validação com MAPE, MAE, RMSE, viés e tempo.
7. `### 08.6 — Ranking e gate`: ganho sobre parâmetros fixos, diferença entre CV e validação, custo computacional e recomendação.

Cada bloco será inserido e executado via MCP em 1–3 células, com inspeção das saídas antes de seguir.

## Critérios de aceite

- [x] A seleção de features da Etapa 05 e a preparação da Etapa 06 são reutilizadas sem mudança.
- [x] Cada fold ajusta seu próprio pré-processamento; o teste não é carregado.
- [x] Versão do Optuna, seed, número de trials, folds e espaços de busca ficam registrados.
- [x] Os dois modelos têm referência sob CV e métricas holdout com as configurações fixas e ajustadas.
- [x] MAPE é a métrica principal; MAE, RMSE, viés e tempo apoiam a decisão.
- [x] Ganhos, limites e custo de tuning são comparados; nenhuma previsão ou modelo é persistido.
- [x] O gate registra hiperparâmetros, recomendações e pendências para a Etapa 09.

## Gate

**Estado:** execução concluída e aprovada pelo usuário em 10/11/2026; Etapa 09 autorizada.

## Evidências e resultados

- Optuna 5.0.0 foi instalado somente no `.venv` do projeto e fixado em `requirements.txt`. A busca usou sampler TPE com seed 42, 20 trials concluídos por algoritmo e `KFold(n_splits=3, shuffle=True, random_state=42)` no treino. O scorer foi MAPE médio.
- O pipeline reajustou imputação e codificação em cada fold. As buscas usaram 12.186 linhas de treino e 40 features; a comparação final usou uma vez as 2.619 linhas de validação. O teste não foi usado para tuning nem avaliação.
- Auditoria final via notebook MCP: 20 trials completos para cada algoritmo; quatro conjuntos de métricas finitos; base de modelagem preservada; arquivo de teste presente com tamanho previamente conferido de 11.634.013 bytes. Auditoria aprovada.
- Custo das buscas: LightGBM 118,84 s; XGBoost 160,83 s.

| Modelo | MAPE CV (%) | MAPE validação (%) | MAE validação (€) | RMSE validação (€) | Viés médio (€) |
|---|---:|---:|---:|---:|---:|
| LightGBM fixo | 27,5255 | 27,3626 | 41,8487 | 180,6271 | -3,3334 |
| LightGBM ajustado | 26,5706 | **26,2694** | **40,3583** | 180,6070 | -3,1121 |
| XGBoost fixo | 27,3673 | 27,3666 | 42,0067 | 185,8790 | -2,0740 |
| XGBoost ajustado | 27,1381 | 27,4542 | 41,8248 | 180,6749 | -2,4942 |

- O tuning do LightGBM melhorou o MAPE de validação em 1,0932 p.p. ante a configuração fixa, com MAE menor; o RMSE ficou praticamente igual.
- O tuning do XGBoost melhorou a CV em 0,2292 p.p., mas piorou o MAPE de validação em 0,0877 p.p. ante a configuração fixa. Manter a configuração fixa como referência desse algoritmo.
- Recomendação para a Etapa 09: LightGBM ajustado como candidato, condicionado à aprovação do gate. Esta escolha decorre do holdout de validação e não representa resultado de teste.

### Melhores parâmetros encontrados

- **LightGBM:** `n_estimators=276`, `learning_rate=0.0348896`, `max_depth=7`, `num_leaves=21`, `min_child_samples=50`, `subsample=0.6298203`, `colsample_bytree=0.9947548`, `reg_alpha=1.2273801`, `reg_lambda=0.0062354`; `subsample_freq=1`, seed 42.
- **XGBoost:** `n_estimators=429`, `learning_rate=0.0131718`, `max_depth=10`, `min_child_weight=9.1131159`, `subsample=0.6330944`, `colsample_bytree=0.7922315`, `gamma=2.1365798`, `reg_alpha=1.1312882`, `reg_lambda=0.1517793`; seed 42.
