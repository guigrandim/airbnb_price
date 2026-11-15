# Etapa 09 V2 — Métricas e recomendador

Data15/11/2026. Execução concluída. Gate09V2 aprovado pelo usuário, com autorização para a Etapa10V2.

## Objetivo

Retreinar o LightGBM congelado em17.021anúncios de desenvolvimento e avaliar a versãoV2 no teste preservado, produzindo referências e faixas em memória.

## Estratégia e premissas

- Congelar36features,pré-processador e parâmetros recomendados08V2 antes de carregar os registros do teste.
- Concatenar treino14.018e validação3.003 na ordem registrada. KFold5 shuffle seed42 para resíduosOOF,com fit completo do pipeline por fold. Calcular quantis5%/95%dos resíduos real−previsão.
- Faixa empírica central90%,condicionada às escolhas anteriores de desenvolvimento. Reportar cobertura global e por segmentos. A amostra e o procedimento não fornecem garantia conformal formal.
- Ajustar pipeline final em todo desenvolvimento antes de ler teste.
- Conferir hash do teste eIDs congelados. LimpezaV2 em cópia,mesmas regras de preço positivo,bairro oficial,exclusões autorizadas,banheiros contextualmente inválidos virandoausentes. Preservar preditores ausentes para pipeline.
- Recriar reviews até06/12/2018 e somente as derivadas usadas pelas36features,com referência geográfica fixa do GeoJSON. Usar esquema e normalização06V2. Não recalcular corte de ausências no teste.
- Prever uma vez nesta avaliaçãoV2 e reportar métricas brutas MAPE,MAE,RMSE,viés,caudas e segmentos. Cache em memória deve impedir repetição acidental da previsão em reexecução da célula.
- Referência indicativa porid,gap€/%e faixa. Previsão bruta<=0 recebe status sem referência utilizável e campos de recomendação ausentes. Essa é a política escolhida para impedir indicação comercial de€0. Preservar previsão bruta nas métricas.
- Arquivo bruto preservado porhash e recomendações somente em memória.
- O teste já foi exposto no fluxo histórico e em auditorias de qualidade. Reportar o desempenhoV2 como avaliação no holdout histórico após congelamento,com essa limitação de independência. Nenhuma revisão do modelo será feita olhando a saída desta etapa.

## Células previstas

1. Congelamento,contrato eOOF.
2. Ajuste final no desenvolvimento.
3. Teste bruto,limpeza,reviews e reconciliação.
4. Engenharia e conferência do esquema.
5. Avaliação cacheada,métricas,recomendações e cobertura.
6. Auditoria,interpretação e gate.

## Critérios de aceite

- Parâmetros/36features correspondem ao gate08V2.
- OOF e ajuste final limitados ao desenvolvimento. Nomes eIDs alinhados.
- Limpeza de teste reconciliada e mesmo esquema36,nulos preservados.
- Métricas calculadas das previsões brutas,faixa congelada antes do teste e cobertura segmentada.
- Referências porid auditáveis e abstenção explícita se previsão<=0.
- Hash original confirmado e resultados salvos no notebook. Gate09V2 antes de10V2.

## Evidências e gate

- OOF310 completou5folds,17.021previsões,MAPE27,172418%. Quantis real−previsão de−€75,15351792e+€83,26526509. É faixa empírica condicionada ao desenvolvimento.
- Pipeline final312 ajustado em17.021×36,com132colunas codificadas,em1,70s. Parâmetros completos iguais ao candidato aprovado08V2.
- Teste bruto3.005×96,IDs congelados ehash conferidos. Nenhuma linha removida pelas regrasV2.2.562casos completos históricos identificados e443incompletos preservados. Engenharia316 resultou em3.005×36,com1.784células ausentes,398anúncios sem histórico auxiliar. Reviews com0datas inválidas e0futuras. Matriz transformada3.005×132finita.
- Uma previsãoV2 gerada e guardada em cache318. Métricas brutas n3.005,MAPE25,9829%,MAE€38,9534,RMSE€105,3184,viés−€1,1601,APEp9575,1440%,p99146,3594%. Zero previsões não positivas. Recomendações em memória3.005×11.
- Cobertura global90,715%,largura média€158,001. TipoEntire home/apt n2.421,MAPE24,2450%,cobertura89,8802%. Private room n578,MAPE32,6191%,cobertura94,1176%. Shared room n6,MAPE87,9666%,cobertura100%,amostra insuficiente para interpretação estável.
- Sem histórico n398,MAPE37,1753%,cobertura81,6583%. Com histórico n2.607,MAPE24,2742%,cobertura92,0982%. A faixa global não atingiu cobertura nominal em todos os segmentos.
- Quartis definidos no desenvolvimento em€95/€125/€175. Q1 n681,MAPE45,3554%,viés+€28,3882,cobertura94,8605%. Q4 n763,MAPE23,4890%,viés−€47,9701,cobertura74,1809%. Não recalibrar faixa ou preço usando esses resultados do teste.
- Na população completa histórica n2.562,o modeloV2 teveMAPE24,0174%,MAE€34,6324,RMSE€79,0915. Nas443linhas antes excluídas,MAPE37,3501%,MAE€63,9431,RMSE€197,6432. As métricas globaisV2 incluem público maior que o fluxo histórico.
- Gap mediano€6,801e5,619%,referência acima do anunciado em58,702%doscasos. Diferenças são indicativas do preço anunciado do snapshot. Receita/uplift dependem da etapa econômica.
- Auditoria320 válida. IDs únicos/disjuntos,dados de desenvolvimento preservados,cache conferido eSHA-256antes/depois12b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178.

## Política e limites de uso

Recomendador apresenta preço de referência e faixa empírica global do snapshot. Previsões não positivas recebem abstenção,embora nenhum caso tenha ocorrido no testeV2. Coberturas segmentadas e erro de públicos sem histórico acompanham a avaliação. O gap frente ao anunciado não estima preço ótimo ou efeito causal.

A faixa tem cobertura insuficiente nos caros e sem histórico. Esses achados são limitações avaliadas no teste,sem recalibração posterior. Uma revisão de incerteza exigiria novo plano usando somente desenvolvimento e aprovação específica. Não confundir cobertura90,715%global com garantia individual.

## Gate

Revisão independente do subagente nas células309–320 e neste plano sem bloqueio técnico. Conferiu esquema, congelamento, OOF, métricas, política e integridade. Ressalva operacional para futuras alterações do pré-processador, cuja configuração não integra a chave do cache. Invalidar o cache nessa situação. Não houve divergência nesta execução.

Verificação final confirmou notebook salvo com322células, seis células de código desta etapa executadas sem erros, sem funções/classes/lambdas próprias e hash do teste preservado. `git diff --check` sem erros de whitespace.

Etapa09V2 aprovada pelo usuário em15/11/2026. Última etapa aprovada09V2. Etapa10V2 autorizada. Teste histórico já observado,condição de independência registrada. Pipeline,recomendações,cacheOOF eprevisões permanecem em memória.
