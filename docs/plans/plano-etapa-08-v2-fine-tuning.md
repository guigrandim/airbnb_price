# Etapa 08 V2 — Fine tuning bayesiano

Data 15/11/2026. Etapa08V2 aprovada pelo usuário. Etapa09V2 autorizada com LightGBM ajustado e36features.

## Objetivo

Ajustar XGBoost e LightGBM sobre as36features e comparar custo-benefício com as configurações fixas da Etapa07V2.

## Estratégia e premissas

- Treino14.018linhas, validação3.003. Teste conferido somente por hash. Dados,features e limpeza congelados.
- Optuna TPE(seed42),20trials sequenciais por algoritmo,KFold3 shuffle seed42 no treino. Critério de término20trials. Cada trial limitado a600árvores e profundidade especificada abaixo. Quatro threads por estimador,folds sequenciais.
- MAPE médio dos folds como objetivo. Reajustar clones completos do pipeline, incluindo imputação, indicadores e encoder, em cada parte de ajuste.
- Usar36features aprovadas como contrato fixo. A seleção anterior faz parte do desenvolvimento, logo CV é referência interna condicionada a escolhas anteriores. Nenhum novo seletor supervisionado fora dos folds.
- Fluxo study.ask/study.tell em loops sequenciais, sem funções/classes/lambdas no notebook.
- Calcular CV de referência dos dois modelos fixos sob os mesmos folds antes da busca.
- LightGBM n_estimators150–600,learning_rate0,01–0,10log,max_depth4–12,num_leaves15–min(63,2**max_depth),min_child_samples10–60,subsample e colsample0,60–1,00,reg_alpha/reg_lambda0,001–10log. Fixar subsample_freq1,seed42.
- XGBoost n_estimators150–600,learning_rate0,01–0,10log,max_depth3–10,min_child_weight1–10log,subsample e colsample0,60–1,00,gamma0–5,reg_alpha/reg_lambda0,001–10log. Fixar hist,objetivo squared-error,seed42.
- Ao terminar ambas buscas, ajustar vencedores no treino completo e avaliar validação. Reutilizar previsões fixas da07 para comparação. Métricas brutas MAPE,MAE,RMSE,viés,caudas e segmentos com/sem histórico.
- Recomendar candidato com base no ganho, risco e custo, registrando parâmetros completos. Manter estudos,modelos e previsões em memória.

## Células previstas

1. Entrada,dependências,versões e referências CV.
2. Busca LightGBM e inspeção.
3. Busca XGBoost e inspeção.
4. Comparação fixo/ajustado em validação e segmentos.
5. Auditoria,decisões,limitações e gate.

## Critérios de aceite

-20trials completos por algoritmo com parâmetros,MAPE CV e duração registrados.
- Pré-processamento ajustado nos folds de treino. Validação fora do objetivo da busca.
- Referências fixas e ajustadas com mesma população,sem clipping de previsões.
- Fontes e teste íntegros. Saídas salvas no notebook e plano atualizado.
- Gate08V2 antes de09V2.

## Evidências e gate

- Optuna5.0.0 disponível. Entrada e fonte aprovadas conferidas. CV fixa LightGBM28,5395%(std0,7649),XGBoost27,8502%(std0,9338).
- LightGBM concluiu20trials. Melhor MAPE CV27,156365%,trial18,em83,87s. Parâmetros max_depth11,n_estimators342,learning_rate0,01711034587,num_leaves59,min_child_samples51,subsample0,6110368302,colsample_bytree0,8065093639,reg_alpha0,1085696595,reg_lambda0,01044826615. Fixos seed42,n_jobs4,subsample_freq1,objective regression.
- XGBoost concluiu20trials em176,04s. Vencedortrial14,MAPECV27,735663%. Parâmetros n_estimators429,learning_rate0,01374743804,max_depth10,min_child_weight9,06836672,subsample0,6330944131,colsample_bytree0,9202067524,gamma2,460367479,reg_alpha1,345273058,reg_lambda0,1518111039. Fixos seed42,n_jobs4,hist,objective squared-error.
- Duração total das buscas259,90s. As duas têm20trialsCOMPLETE e scores por fold armazenados em user_attrs. Tempos e parâmetros completos estão no notebook e nos estudos em memória.

| Configuração | MAPE CV (%) | MAPE validação (%) | MAE (€) | RMSE (€) | Viés (€) |
|---|---:|---:|---:|---:|---:|
| LightGBM fixo |28,5395|29,4266|43,9089|174,5383|−1,4377|
| LightGBM ajustado |27,1564|27,7659|41,6772|173,9412|−1,6244|
| XGBoost fixo |27,8502|29,1213|43,3946|178,9912|−0,1045|
| XGBoost ajustado |27,7357|28,1256|42,4274|176,1546|−1,2578|

- GanhoLightGBM de1,6607p.p.emMAPEval e€2,2318emMAE. GanhoXGBoost de0,9957p.p.e€0,9672. Gap treino/validação do LGB caiu de5,6552para3,3996p.p.,eXGBde8,4287para5,9923p.p.
- LGBajustado teveMAPE25,7620%nos2.659anúncios com histórico e43,2553%nos344sem histórico. XGBajustado26,4431%e41,1311%,respectivamente. Candidato globalLGB,com limitação explícita de maior erro e menor desempenho relativo no grupo sem histórico.
- APEp95/p99val do LGBajustado78,7397%/148,5881%;XGB77,9843%/153,3485%. Ambos produziram zero previsões não positivas na validação. Erros de cauda permanecem relevantes.
- Candidato recomendado e parâmetros congelados em `v208_recommended_name`/`v208_recommended_params`. Estudos e pipelines ajustados apenas em treino, mantidos em memória.
- Auditoria307 válida com40trials completos,24linhas de métricas e4configurações globais de validação. FonteV2 preservada,ID20644162ausente,template de preparação semfit eSHA-256doteste12b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178.

## Limites e gate

Revisão estática independente das células298–307 concluída sem bug concreto na busca ou avaliação. Validação já usada em escolhas das Etapas05/07 e agora na comparação final08,portanto27,7659%é resultado de desenvolvimento sujeito à seleção. MelhorCVentre20trials também é estimativa interna otimizada.

Recomendar LightGBM ajustado para09V2 peloMAPEglobal eMAE. CV interna condicionada às escolhas anteriores de features/população. Orçamento20trials limita exploração e não demonstra ótimo global. MAPE mede distância ao preço anunciado do snapshot.

Gate08V2 pendente. Última etapa aprovada07V2. Nenhuma avaliação do teste ou implementação09V2 nesta execução.
