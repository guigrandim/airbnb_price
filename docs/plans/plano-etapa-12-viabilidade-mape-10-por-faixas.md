# Etapa 12 — Viabilidade da meta de MAPE 10% por faixas

Data: 16/11/2026. Status: Etapa 12 aprovada pelo usuário em 16/11/2026; Etapa 13 ainda sem escopo definido e não iniciada.

## Objetivo

Avaliar se 10% de MAPE é plausível para o modelo de preços e localizar segmentos e anúncios que mais contribuem para o erro, usando previsões fora da amostra no conjunto de desenvolvimento.

## Escopo e premissas

- O projeto V2 está encerrado, com a Etapa 11 aprovada. Esta investigação é uma etapa adicional solicitada pelo usuário.
- Manter o pipeline aprovado, as 36 features e as partições existentes como referência inicial. Não sobrescrever artefatos aprovados.
- Usar previsões OOF do desenvolvimento para novas decisões. O teste já foi consultado; não será usado para escolher faixas, remover linhas, ajustar o roteamento ou selecionar modelos.
- Analisar MAPE por faixas do preço real para diagnóstico, junto de n, MAE, RMSE, viés, percentis do erro percentual e contribuição de cada faixa para o MAPE global.
- Investigar os maiores erros por anúncio com contexto das features. Sinalizar possíveis erros de registro separadamente de anúncios legítimos incomuns; não excluir casos só para baixar a métrica.
- Se a análise justificar modelos especializados por faixa, atribuir a faixa de inferência pela previsão de um modelo geral, nunca pelo preço real indisponível no momento da recomendação. Comparar com o modelo geral em folds OOF idênticos e sem consultar o teste.
- A meta de 10% será tratada como objetivo, não como resultado prometido. O snapshot é de dezembro de 2018 e não representa o mercado atual.

## Estratégia

1. Confirmar via MCP o notebook, o kernel, o estado dos objetos e o contrato V2 antes de qualquer bloco analítico.
2. Como o kernel reiniciado não contém o cache OOF por anúncio, reconstruir em células novas a base de desenvolvimento e as 36 features pelas regras V2 aprovadas, sem alterar outputs das etapas históricas e sem ler a tabela de teste.
3. Recalcular previsões OOF do LightGBM V2 com os parâmetros aprovados e folds seed42; registrar que o Python ativo difere da versão de treinamento gravada no artefato.
4. Calcular métricas por faixas do preço observado com cortes determinados exclusivamente no desenvolvimento; incluir a contribuição ponderada ao MAPE global.
5. Inspecionar anúncios com maiores erros absolutos e percentuais, exibindo somente campos necessários para auditoria e mantendo as observações na população.
6. Comparar o modelo geral com uma alternativa por faixas apenas se houver suporte amostral. A faixa de roteamento em validação será obtida da previsão do modelo geral; os especialistas serão ajustados apenas nos folds de treino.
7. Interpretar a distância até 10%, a estabilidade entre folds e os segmentos onde a meta pode ou não ser plausível. Encerrar com limitações e gate.

## Células previstas

1. `## Etapa 12 — Viabilidade da meta de MAPE 10% por faixas` e `### 12.1 — Verificação do kernel e do contrato OOF`: estado da sessão, disponibilidade do cache, partições e versões.
2. `### 12.2 — Verificação da base de desenvolvimento reconstruída`: partições por ID, regra V2 de limpeza e reviews, apenas em memória.
3. `### 12.3 — Verificação das 36 features V2`: fórmulas aprovadas, alinhamento de IDs/alvos e exclusão de campos de vazamento.
4. `### 12.4 — Verificação do pré-processador V2`: tipos, imputação, indicadores de ausência e encoding dentro dos folds.
5. `### 12.5 — Verificação das previsões OOF V2`: parâmetros LightGBM congelados e novos scores OOF no desenvolvimento.
6. `### 12.6 — Verificação do MAPE por faixa de preço`: métricas e contribuição por faixa, usando somente desenvolvimento/OOF.
7. `### 12.7 — Verificação dos anúncios com maior erro`: tabela auditável de erros e atributos contextuais, sem exclusões automáticas.
8. `### 12.8 — Verificação de modelos especializados`: experimento OOF com roteamento por previsão, condicionado à suficiência da amostra e ao ganho nas mesmas partições.
9. `### 12.9 — Verificação final e gate`: conclusão sobre viabilidade, evidências, riscos, pendências e decisão.

## Critérios de aceite

- A métrica OOF global é reconciliada com a evidência aprovada antes de qualquer comparação.
- Cada faixa informa corte, tamanho, MAPE, MAE, RMSE, viés, cauda e contribuição ao MAPE total.
- Toda previsão comparada foi produzida fora do fold de ajuste; o teste não participa de nenhuma decisão nova.
- A lista de casos influentes não transforma valores extremos legítimos em erros de dados sem evidência verificável.
- Modelos especializados, se avaliados, são roteados apenas por informação disponível na inferência e comparados nas mesmas partições.
- A conclusão separa resultado observado, hipótese de melhoria e limite de generalização do snapshot de 2018.
- Alterações no notebook ocorrem em blocos curtos via MCP, com saída inspecionada após cada bloco.

## Evidências prévias e limitações

- Plano V2 da Etapa 09 registra 17.021 previsões OOF com MAPE de 27,172418%.
- A avaliação histórica V2 registrou 3.005 anúncios no teste, MAPE de 25,9829%. Esse teste já foi consultado e não será reutilizado na investigação.
- Faixas do teste definidas no desenvolvimento em €95/€125/€175: Q1 n=681, MAPE 45,3554%; Q4 n=763, MAPE 23,4890%. São evidências descritivas existentes, não validação de alterações.
- O OOF anterior exigiu redução aproximada de 63% no MAPE para chegar a 10%; isso quantifica a distância matemática, não prova impossibilidade.
- O plano de Etapa 11 registra aprovação em 15/11/2026 e fechamento do projeto.

## Estado do gate no checkpoint inicial

- Pedido do usuário em 16/11/2026: investigar a meta de 10%, testar o desempenho por faixas e identificar possíveis anúncios que prejudicam o modelo.
- Após reiniciar o VS Code, a sessão passou a expor comandos MCP de leitura, edição e execução de células.
- Fluxo de validação concluído: leitura de célula; inserção e execução de `print("MCP Jupyter validado:", 1 + 1)`; inspeção da saída `MCP Jupyter validado: 2`; remoção da célula temporária; salvamento pelo MCP.
- Notebook com 339 células antes da nova etapa; a seção final registra a Etapa 11 aprovada e o projeto encerrado.
- Célula 12.1 executada: kernel Python 3.13.17 em `.venv`, sem os objetos `v209_*` do OOF; as saídas persistidas mostram apenas métricas agregadas, não os vetores por anúncio. O Python do artefato registra 3.10.4; `py -3.10` também tem LightGBM 4.6.0, enquanto o ambiente ativo tem 4.7.0. A reexecução será tratada como diagnóstico novo e terá as versões explícitas.
- Nenhum pacote ou configuração foi instalado/modificado. O teste bruto não foi lido como tabela; a checagem 12.1 não consultou dados de teste.
- Célula 12.2 executada: população V2 reconciliada em 17.021 anúncios (14.018 treino, 3.003 validação); exclusões observadas no desenvolvimento foram 2 preços inválidos, 1 `maximum_nights` e 1 ID autorizado; 3 banheiros convertidos em ausentes; 0 reviews inválidas/futuras; CSV separado do teste não aberto.
- Célula 12.3 executada: base de features 17.021×52; bloco aprovado `capacidade_comercial` com 36 preditores; matriz 17.021×36, separada em 14.018 treino e 3.003 validação. Parsing de comodidades sem erros; alvo e ID fora das preditoras; ponto geográfico fixo 52.3544265, 4.9169995.
- Status no checkpoint 12.3: base e features V2 reconstruídas; etapas analíticas ainda pendentes.

## Evidências finais da execução

- A validação de estado do MCP encontrou o kernel listado como busy, mas comandos diretos no kernel responderam; o ping de execução concluiu e a célula final terminou. Nenhum reinício do kernel foi necessário. O notebook foi salvo pelo MCP com 360 células e isDirty=false.
- Célula 12.4: pré-processador não ajustado antes dos folds; 23 colunas contínuas, 4 binárias e 9 categóricas; Python 3.13.17, scikit-learn 1.7.2 e LightGBM 4.7.0.
- Célula 12.5: 17.021 previsões OOF em KFold5 shuffle seed42; MAPE 27,172418%, igual ao registro aprovado; MAE €39,602, RMSE €128,6714 e viés −€0,0225. Os cinco folds cobriram cada linha uma vez; nenhuma previsão não positiva.
- Célula 12.6: faixas reais de desenvolvimento — até €95: n=4.307, MAPE 44,149%, contribuição 11,171 p.p. (41,113% do total), viés +€27,661; €95–€125: n=4.303, MAPE 21,818%, contribuição 5,516 p.p. (20,299%), viés +€17,088; €125–€175: n=4.330, MAPE 18,961%, contribuição 4,823 p.p. (17,751%), viés +€2,947; acima de €175: n=4.081, MAPE 23,615%, contribuição 5,662 p.p. (20,837%), viés −€50,432 e RMSE €252,732. A soma das contribuições reproduziu o MAPE global.
- Célula 12.7: os 20 maiores erros percentuais e os 20 maiores erros absolutos foram listados com contexto. O top 1%, 5% e 10% de APE concentram 9,092%, 24,045% e 36,162% do MAPE, respectivamente; 460 anúncios têm APE ≥100%, com participação de 16,561% no MAPE.
- Célula 12.8: 40 IDs dos dois rankings foram confrontados com o preço original em listings_details.csv; todos coincidiram após parsing. Exemplo: preço original de $8,500.00 corresponde a €8.500 após a convenção já usada no projeto. Isso elimina erro de conversão nos candidatos, mas não comprova validade comercial do valor.
- Célula 12.9: especialistas por quatro faixas foram treinados dentro de cada fold; o roteamento no holdout usou só a previsão OOF do generalista. O MAPE subiu para 32,033883% (+4,861465 p.p.); piorou nos cinco folds e em cada faixa real. Não recomendar essa alternativa.
- Célula 12.10: reduzir de 27,172418% para 10% exige −17,172418 p.p. ou 63,198% de redução relativa. Mesmo zerando hipoteticamente o APE do decil superior, o MAPE remanescente seria 17,346%, mantendo erros dos demais anúncios. Este é um limite ilustrativo, não uma previsão de resultado.
- O holdout de teste, seus alvos e métricas não participaram das análises novas. IDs de partição foram reconstruídos para reproduzir as partições. O teste histórico já observado continua sendo evidência descritiva prévia, não critério de seleção.
- A investigação não alterou resultados V2 aprovados, dados brutos ou artefatos de modelo; nenhuma linha foi excluída. A diferença de versões do Python/LightGBM limita a reprodução bit a bit, embora o MAPE OOF tenha coincidido.
- O plano original previa modelos especializados em 12.8 e gate em 12.9. A checagem adicional do preço de origem ocupou 12.8; a comparação de especialistas e o gate passaram a 12.9 e 12.10.

## Conclusão e estado do gate

- Conclusão: a meta de 10% não é sustentada pelo desempenho do modelo e pela segmentação testada. Não se prova impossibilidade com outros dados ou métodos; a meta requer nova pesquisa e validação independente.
- Decisão: manter o generalista V2 como referência atual; não excluir preços só para melhorar MAPE; tratar os extremos como candidatos a validação de negócio, não como erros confirmados.
- Status atual: Etapa 12 aprovada pelo usuário em 16/11/2026. Última etapa aprovada: Etapa 12.
- Pendência: definir e planejar o escopo da Etapa 13; nenhuma execução começou.


## Registro da aprovação do gate

- Em 16/11/2026, o usuário respondeu “Aprovo” à pergunta de aprovação da Etapa 12 para avançar à Etapa 13.
- Etapa 12 aprovada; última etapa aprovada: Etapa 12 (investigação adicional após Etapa 11 V2).
- Etapa 13 não consta no fluxo existente. Nenhuma implementação da Etapa 13 foi iniciada; seu escopo depende da escolha e do plano formal antes das células.

