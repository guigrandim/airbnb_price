# Etapa 10 — Resultado Econômico Final

**Status:** análise concluída em 12/11/2026; gate financeiro pendente por falta de insumos aprovados para EV e ROI.

## Objetivo

Este registro preserva a análise histórica. A atualização após a auditoria dos dados está em [Etapa 10 V2](plano-etapa-10-v2-resultado-economico-final.md), com população ampliada, previsões congeladas V2 e sensibilidade ao proxy de noites.

Reavaliar o business case com o desempenho e os gaps da Etapa 09, estimar o GMV-base segundo as regras documentadas do projeto e calcular EV/ROI somente quando os insumos financeiros aprovados estiverem disponíveis.

## Escopo e premissas

- Usar o snapshot de Amsterdam de 06/12/2018 e o modelo final congelado da Etapa 09. Por autorização do usuário, a execução integral reproduziu as previsões e métricas aprovadas; nenhuma feature, hiperparâmetro ou regra de recomendação foi alterada.
- Resultados aprovados da Etapa 09: 2.562 casos de teste; MAPE 25,1276%; MAE €36,4427; RMSE €79,3473; viés −€0,3551; cobertura observada da faixa 90,20%.
- O kernel perdeu as previsões OOF, previsões de teste e tabela completa de recomendações. O usuário autorizou executar todo o notebook para reconstruir esses objetos usando as células aprovadas. Isso é uma reprodução auditável; não alterar features, parâmetros, limpeza ou regra de recomendação. As métricas reproduzidas coincidiram com as evidências salvas da Etapa 09.
- Proteger `data/processed/df_test_raw.csv` durante a reexecução: confirmar o SHA-256 original `12b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178`, manter os bytes em memória antes de executar e verificar/restaurar o arquivo ao final.
- A regra do projeto estima reservas por avaliações ÷ 50%, noites por reservas × duração média (3 noites como fallback, respeitando `minimum_nights`) e limita noites anuais a 70% da capacidade. São estimativas por proxy, não vendas observadas.
- O plano aprovado da Etapa 01 registra que GMV, EV e ROI não foram calculados. Até o início da Etapa 10, não foi localizado baseline financeiro com taxa de monetização, adoção, elasticidade, custos ou limites legais por categoria.
- Não inventar premissas ausentes. Calcular EV/ROI numéricos apenas com valores aprovados/documentados; caso contrário, apresentar fórmulas condicionais, insumos faltantes e manter o gate pendente.
- A diferença entre preço de referência previsto e preço anunciado não é uplift causal. Sem reservas/faturamento ou experimento, todo retorno é projetado e condicionado às premissas.
- Manter resultados em memória e no notebook; não exportar dados ou recomendações.

## Estratégia

1. Registrar a autorização do usuário e inserir uma salvaguarda via MCP que preserve os bytes do teste e valide seu hash.
2. Executar as células aprovadas via MCP para reconstruir OOF, recomendações e saídas da Etapa 09. Comparar as métricas aprovadas e conferir o hash do arquivo bruto; registrar que a reprodução executou novamente a avaliação congelada do teste.
3. Alinhar as previsões OOF aos IDs de desenvolvimento, verificando que preços e features correspondem à ordem usada na calibração. Unir essas recomendações à saída do teste e resumir os gaps por partição e no total.
4. Estimar noites para 12 meses por anúncio: avaliações nos últimos 365 dias ÷ 50%, multiplicadas por `max(3 noites, minimum_nights)`, com teto de 70% de 365 noites. Calcular GMV-base em euros para os casos completos elegíveis; informar que é proxy, não reserva observada.
5. Calcular GMV com preço de referência e ΔGMV mantendo noites constantes e supondo aplicação integral apenas como cenário ilustrativo. Não chamar o resultado de uplift causal ou EV; sem adoção aprovada, elasticidade, monetização e custo, EV/ROI em euros permanecem indeterminados.
6. Apresentar `EV(MAPE)` em 8%, 15%, 25,1276% e 40% como fatores condicionais. A fórmula linear `V_max × max(0, 1 − m)` será identificada como cenário ilustrativo, nunca como fração de receita empiricamente recuperada.
7. Comparar com o business case inicial somente se houver valores de referência salvos; separar mudança metodológica de desempenho e registrar evidências necessárias para A/B test.

## Células previstas

1. `## Etapa 10 — Resultado Econômico Final`: aprovação, escopo e limites de interpretação.
2. `### 10.1 — Verificação dos resultados e insumos`: autorização da reprodução, disponibilidade dos resultados Stage09 e insumos financeiros documentados.
3. `### 10.2 — EV por MAPE: cenário ilustrativo`: multiplicadores algébricos e explicação de por que não equivalem a receita.
4. `### 10.3 — Gaps e GMV por proxy`: distribuição OOF + teste, cálculo de noites, GMV-base e cenário de preço constante.
5. Tabela de insumos financeiros ainda necessários para EV/ROI.
6. `### 10.4 — Comparabilidade e evidência econômica`: comparação possível e condições que impedem alegação de retorno realizado.
7. `### 10.5 — Auditoria e gate`: consistência, decisões, pendências e status.
8. Células de salvaguarda temporárias antes da gravação do teste e ao final da reprodução integral.

As células serão inseridas e executadas via MCP em blocos de 1–3. O código terá comentários em português e não definirá funções, classes ou lambdas.

## Critérios de aceite

- [x] A reprodução usou as células e regras aprovadas, recuperou previsões e gaps, e reproduziu as métricas salvas da Etapa 09.
- [x] O SHA-256 do arquivo bruto do teste foi validado antes e depois da reprodução; os bytes originais permaneceram intactos.
- [x] A distribuição integral de gaps usa previsões OOF do desenvolvimento e recomendações do teste, com IDs e preços alinhados e sem interpretação causal.
- [x] O GMV-base por proxy usa 12 meses, avaliações ÷ 50%, `max(3, minimum_nights)` noites por estadia e teto de 70% da capacidade; população e moeda estão explícitas.
- [x] GMV recomendado e ΔGMV são apresentados somente como cenário de preço sob noites constantes e aplicação integral; não são tratados como EV ou retorno realizado.
- [x] A ausência de base numérica aprovada foi declarada; nenhum GMV, EV ou ROI foi inventado.
- [x] O cenário algébrico de MAPE separa o desempenho medido das hipóteses financeiras e não o apresenta como recuperação empírica de receita.
- [x] Nenhuma projeção é chamada de retorno realizado sem dados de reservas/faturamento ou experimento.
- [x] O delta versus a Etapa 01 não foi calculado porque não existe business case financeiro aprovado para comparação.
- [x] A evidência necessária para validar uplift com A/B test está registrada.
- [x] A Etapa 11 não foi iniciada sem aprovação do gate da Etapa 10.

## Gate

**Estado:** análise técnica e projeções por proxy concluídas; gate financeiro pendente. A Etapa 11 não foi iniciada.

## Evidências, decisões e pendências

- O usuário aprovou a Etapa 09 e autorizou a Etapa 10 em 12/11/2026. O status de aprovação foi registrado no plano e na seção final do notebook.
- A inspeção de `plano-etapa-01-definicao-problema-preditivo.md` e das células da Etapa 01 confirmou que o business case inicial não calculou GMV, EV ou ROI. Não foram localizados taxa efetiva de monetização, adoção, elasticidade, custos ou limites legais por categoria nos planos/notebook consultados.
- O kernel atual não mantém os objetos da Etapa 09: `stage09_test_predictions`, `stage09_oof_predictions`, `stage09_oof_residuals` e `df_price_recommendations` não estão disponíveis. O notebook preserva os resultados agregados e apenas 10 exemplos de recomendação; a distribuição completa dos gaps não foi exportada.
- Em 12/11/2026, o usuário autorizou explicitamente a execução integral do notebook para recuperar esses resultados. A reexecução deve ser reproduzível e auditada, sem retuning ou alteração dos resultados aprovados; o arquivo bruto do teste será protegido pelo hash `12b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178`.
- A primeira execução integral parou na célula 05.2 porque a lista de 41 features era definida na célula 05.2.1 posterior. Sem editar código ou alterar seleção, a verificação 05.2.1 foi executada antes da célula Boruta; a equivalência entre `host_since` e `host_tenure_years` foi exata (diferença máxima 0), e as contagens/seleção coincidiram com o plano aprovado. O restante foi retomado em ordem via MCP.
- As etapas 05–09 foram reproduzidas: Boruta confirmou as mesmas contagens por fold; comparação de features MAPE 28,5766%/36,0176%; permutação OOF MAPE 27,73% e MAE €39,22; ranking da Etapa 07 reproduzido; buscas Optuna terminaram com os mesmos parâmetros e métricas registrados; OOF MAPE 26,911% e quantis −€74,1041/+€81,6084.
- A avaliação de teste reproduziu exatamente `n=2.562`, MAPE 25,1276%, MAE €36,4427, RMSE €79,3473 e viés −€0,3551. A tabela `df_price_recommendations` voltou à memória com 2.562 anúncios. As contagens de limpeza também coincidiram: 4 linhas com `bathrooms` ausente e 439 com outras ausências.
- O hash do teste antes e depois da avaliação permaneceu `12b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178`; nenhuma restauração de bytes foi necessária.
- A tabela executada mostra somente os fatores ilustrativos `EV/V_max`: 0,92 em MAPE 8%; 0,85 em 15%; 0,7487 em 25,1276%; 0,60 em 40%. Sem `V_max` e custo total, EV em euros e ROI permanecem indeterminados. `1 − MAPE` não é uma fração de receita empiricamente recuperada.
- A Etapa 01 não contém um business case financeiro aprovado para comparar. Na Etapa 10, GMV-base e ΔGMV foram calculados apenas como proxies condicionais; receita incremental da plataforma, EV numérico e ROI não foram calculados. O retorno não pode ser chamado de realizado sem reservas/faturamento observados ou experimento.
- A distribuição combinada de 17.367 gaps foi calculada: mediana do gap €6,78; mediana do gap absoluto €23,82; preço de referência acima do anunciado em 58,2% dos casos. No teste isolado (2.562 anúncios), referência acima em 57,8%, gap mediano +€6,07 e gap absoluto mediano €22,71.
- O proxy anual estimou 855.363,5 noites, GMV-base de €116.592.776 e cenário com preço de referência de aproximadamente €118,48 milhões; ΔGMV proxy de +€1.884.510,85. No teste isolado, o ΔGMV proxy foi −€105.215,21. O cenário supõe aplicação integral e noites constantes; não mede resposta da demanda nem uplift causal.
- A sensibilidade do MAPE foi executada: multiplicadores algébricos de `V_max` 0,92; 0,85; 0,7487; e 0,60 para MAPE 8%, 15%, 25,1276% e 40%. Como `V_max` não foi aprovado/documentado, esses fatores não geram EV em euros.
- Permanecem pendentes taxa de monetização, adoção, elasticidade/resposta da demanda, custo total e população legalmente elegível. Sem receita incremental da plataforma e custo total, ROI numérico não é calculável. Não há reservas/faturamento realizados para validar retorno.
- A Etapa 10 não foi aprovada para a Etapa 11; aguarda decisão sobre premissas e gate financeiro.
