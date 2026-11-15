# Revisão autorizada — Etapas 02, 04 e 03

Data: 15/11/2026. Status: revisão V2 aprovada pelo usuário; Etapa05 V2 autorizada. Em seguida, usuário autorizou remover o ID20644162 (preço €8,3camas,2banheiros). Resultados CV anteriores abaixo precedem essa remoção e são históricos.

## Objetivo

Ampliar cobertura de anúncios válidos e comparar atributos candidatos em treino/CV, conservando os resultados anteriores como baseline histórico.

## Estratégia e premissas

- Bases V2 apenas em memória, sem CSV. Mesmos IDs e seed42; teste bruto intocado e sem avaliação nesta revisão.
- Ruling: implementar em seções V2 após a auditoria; não substituir variáveis históricas que alimentam etapas05–10 com contratos fixos. A integração dessas etapas exige novo gate.
- Etapa02: preservar ausências de preditores, preço positivo, bairro oficial. Valores de banheiro contextualmente inválidos (três IDs auditados) viram ausentes, sem inventar substituto. Manter exclusão expressa do ID7447773 com maximum_nights9999. Zero banheiros e preços extremos permanecem.
- Corte estrito <30% medido apenas no treino; candidatas: camas, tipo de cama, comodidades, política de cancelamento, hóspedes incluídos, taxa extra, limpeza, contagem local de anúncios e verificações do anfitrião. security_deposit fica fora; notas componentes ficam para experimento posterior, por redundância e custo.
- Reviews: agregar eventos até06/12/2018, sem deduplicar anúncio/data. Zero recente é zero eventos; recência sem histórico é ausente. Não usar calendário.
- Etapa04: ausências, retenção, extremos e cinco hipóteses no treino; Pearson e Cramér para dependência; não excluir por correlação ou p-valor.
- Etapa03: conjunto simples sem duplicações monotônicas, indicadores de ausência/histórico, camas/hóspede e comodidades com parser validado. Distância usa referência fixa proveniente do GeoJSON, sem estatística dos folds.
- Comparação: 3 folds treino seed42, RandomForest de orçamento fixo, pipelines com imputação/onehot; comparar base simples, capacidade/comercial e comodidades; comparar população completa histórica versus ampliada na interseção e nos sem histórico. Diagnóstico não é tuning nem resultado final.

## Células previstas

1. Markdown Etapa02 V2 + leitura, limpeza, joins e reconciliação.
2. Markdown Etapa04 V2 + EDA de treino e interpretação.
3. Markdown Etapa03 V2 + features, domínios e comparação por blocos.
4. Conclusão com evidências, limitações e gate.

## Aceite e gate

- IDs únicos, partições disjuntas, preço positivo, exclusões reconciliadas.
- Todas as candidatas retidas passam corte de treino; nulos continuam disponíveis para pipeline.
- Eventos e cardinalidade dos joins auditados; parser de amenities não descarta erros silenciosamente.
- Preprocessamento por fold e métricas por população; nenhuma alegação de melhor conjunto sem comparação.
- Hash do teste antes/depois igual. Etapa11 não iniciada. Não avaliar novamente teste já observado para escolher revisão.

## Execução

- MCP: células253–264, em blocos pequenos; código sequencial sem funções/classes/lambdas. Kernel iniciado anteriormente em Python3.10.4; pandas2.3.3, numpy2.2.6, sklearn1.7.2.
- Base revisada `df_modeling_final_v2`: 17.022×38, treino14.019/validação3.003. Duas linhas removidas por preço inválido e uma pela exclusão autorizada de maximum_nights. Três campos bathrooms invalidados, sem excluir anúncios. Corte <30% no treino manteve as28 entradas candidatas; asserção interrompe uso futuro se o corte descartar campos e os blocos não forem revistos.
- Reviews sem datas inválidas/futuras; merge one-to-one. Histórico auxiliar ausente em2.008 anúncios de desenvolvimento (1.664 no treino). Isso difere de number_of_reviews=0, pois as fontes podem divergir; indicador usa eventos efetivamente disponíveis no auxiliar.
- Engenharia `df_modeling_features_v2`: 17.022×52, incluindo controles/alvo. Blocos de25,36,45 preditores; parser amenities sem erros,24 listas vazias. Centro fixo da envoltória do GeoJSON: latitude52.3544265,longitude4.9169995.
- Cinco hipóteses reavaliadas no treino; heatmaps Pearson/Cramér construídos. Spearman capacidade0,55052, distância−0,17216, comodidades0,21357; superhost efeito0,01130,p0,3984. Não são relações causais.
- Regra de triagem contextual (grupo quarto/bairro/faixa de capacidade com n>=20; preço<25% ou>400% da mediana) sinalizou11 baixos e37 altos, sem excluir. Dez baixos têm camas ou banheiros ao menos na mediana dos pares. Inspecionados textos/condições dos11. ID20644162 (€8,4hóspedes,3camas,2banheiros,descrição120m²) permanece suspeito sem confirmação de erro. Outros textos mencionam barco, estadia longa ou animal; nenhuma correção de preço foi inventada. Flags de preço nunca entram nos preditores.
- RandomForest fixo60árvores,max_depth12,min_samples_leaf5,seed42; CV3 nos mesmos folds. Simples completo: MAPE28,204% na interseção histórica de12.186 anúncios. Simples ampliado:28,161% na interseção/29,936% todos. Capacidade-comercial:27,509%/29,218%. Comodidades:27,538%/29,231%. Imputação e encoder ajustados por fold; validação reservada não usada.
- Capacidade-comercial melhorou o simples ampliado nos três folds da interseção (28,037/27,000/27,490% vs28,628/27,696/28,159%). Comodidades tiveram diferença pequena e inconsistente. Recomendar36features como candidato, não superioridade universal.
- MAPE dos sem histórico auxiliar:40,788% no candidato. Os11 preços baixos sinalizados tiveram MAPE615,689% e contribuição0,483p.p. ao global; não foram excluídos para melhorar métrica.
- Ruling: comparação usa baseline diagnóstico RF simples de25features, não reproduz o LightGBM antigo de40features. Avaliar novamente todo o fluxo selecionado é trabalho das etapas posteriores; não afirmar que já se superou o modelo final anterior.
- Subagente revisou células253–262: nenhum bloqueio crítico de leakage/comparabilidade; correção contratual do corte adicionada e executada. `is_studio` denota zero quartos confirmado; imputador cria indicador de bedrooms ausente.
- Hash teste antes/depois igual `12b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178`. Nenhum CSV ou modelo exportado. Nenhuma previsão no teste repetida.

## Pendências e gate

Atualização15/11/2026: usuário aprovou a revisão e autorizou05V2; em seguida excluiu expressamente ID20644162. Base reconstruída17.021×38 (treino14.018,validação3.003), engenharia17.021×52; EDA atualizada com10preçosbaixos/37altos sinalizados. As contagens/métricas anteriores acima são históricas. Resultado05V2 disponível no [plano de seleção](plano-etapa-05-v2-feature-selection.md); gate05V2 pendente.

Revisão concluída aguardando aprovação do conjunto V2 para revisar Etapa05. Nenhuma integração silenciosa às etapas históricas05–10; seus contratos e resultados não representam a V2. Etapa11 não iniciada. Problemas de ordem Boruta e sobrescrita de teste no fluxo histórico continuam registrados para correção antes de execução linear integral. O teste já conhecido não pode ser tratado como evidência inédita após novas escolhas.
