# Etapa 06 — Preparação dos Dados

**Status:** implementada e verificada em 09/11/2026; gate aguardando aprovação do usuário.

## Objetivo

Revisão V2 executada em15/11/2026 com36features e130colunas transformadas. Ver [plano e evidências06V2](plano-etapa-06-v2-data-preparation.md). O conteúdo abaixo registra o fluxo histórico.

Preparar transformações reproduzíveis para as 40 features recomendadas na Etapa 05, sem ajustar transformadores fora do treino e sem consultar o teste.

## Escopo e premissas

- Usar df_modeling_features após as decisões aprovadas da EDA e as partições congeladas: 12.186 anúncios de treino e 2.619 de validação.
- Usar as 40 features únicas recomendadas: 33 numéricas e 7 categóricas. Excluir accommodates_log1p por redundância confirmada; excluir id, price, particao e host_since bruto.
- A preparação não seleciona novas features, não treina modelos e não calcula MAPE.
- Nenhum dado do arquivo df_test_raw.csv será lido.
- Manter df_modeling_features intacto. Imputação, codificação e escala ficam em pipelines, sem materializar uma matriz limpa fora deles.

## Estratégia

1. Conferir partições, alvo, preditoras, tipos, ausências e colunas proibidas usando somente treino e validação.
2. Separar variáveis numéricas contínuas de indicadores binários conforme o dicionário das features; conferir a separação nos dados de treino.
3. Criar dois ColumnTransformer:
   - Modelos sensíveis à escala: imputação pela mediana e RobustScaler nas numéricas contínuas; preservar indicadores binários em 0/1; imputar categóricas pela moda e aplicar OneHotEncoder(handle_unknown="ignore").
   - Modelos de árvore: mesma imputação e codificação categórica, sem escala numérica.
4. Encapsular as transformações em Pipeline; usar saída esparsa do one-hot para limitar memória.
5. Validar em folds internos do treino: ajustar cada pipeline somente no fold de ajuste, transformar o fold retido e conferir número de linhas, finitude e nomes das colunas transformadas.
6. Ajustar uma cópia de verificação no treino completo apenas para auditar a transformação da validação. Usar transform, nunca fit ou fit_transform, na validação; registrar categorias inéditas ignoradas e a largura final da matriz.
7. Registrar versões e resultados de integridade. Reservar comparação de modelos e métricas para as etapas seguintes.

## Células previstas

1. ## Etapa 06 — Preparação dos Dados: objetivo e limites da etapa.
2. ### 06.1 — Verificação da entrada: contrato das partições, 40 colunas, tipos, ausências e colunas proibidas.
3. ### 06.2 — Grupos numéricos e categóricos: definição auditável das colunas contínuas, binárias e categóricas.
4. ### 06.3 — Pipelines de transformação: imputação, codificação one-hot, escala robusta para contínuas e variante sem escala para árvores.
5. ### 06.4 — Verificação dentro dos folds de treino: ajuste e transformação por fold, sem usar validação ou teste para aprender parâmetros.
6. ### 06.5 — Auditoria da validação: ajuste no treino completo e somente transformação na validação; conferir categorias desconhecidas, dimensões e valores finitos.
7. ### 06.6 — Verificação final e gate: resumir objetos, versões, escopo e limitações, sem treinamento de estimadores.

## Critérios de aceite

- [x] As partições e as 40 features coincidem com a decisão da Etapa 05.
- [x] id, price, particao, host_since bruto e qualquer coluna do teste ficam fora das preditoras.
- [x] Cada transformador aprendido é ajustado somente no treino ou no fold de ajuste.
- [x] A validação recebe somente transform; categorias desconhecidas são aceitas sem erro.
- [x] As duas variantes preservam linhas, geram valores finitos e nomes de saída reproduzíveis.
- [x] Dados de origem permanecem inalterados; nenhum CSV de modelagem ou teste é criado.
- [x] O notebook registra resultados, versões, ressalvas e estado do gate.

## Dependências e ressalvas

- Usar as versões já instaladas e fixadas de pandas, NumPy e scikit-learn; não instalar pacotes sem necessidade.
- RobustScaler foi escolhido para as variáveis contínuas por reduzir a influência de caudas e extremos observados na EDA. Indicadores binários permanecem em 0/1.
- One-hot encoding expande variáveis categóricas; registrar o número de colunas resultante e manter saída esparsa.
- As verificações por folds auditam o ajuste do pré-processamento, não constituem comparação de desempenho de modelos.
- A etapa não confirma melhoria de MAPE; essa avaliação pertence à Etapa 07.


## Evidências da execução

- Entrada: 12.186 linhas de treino e 2.619 de validação; 40 features (33 numéricas e 7 categóricas); alvo positivo e sem ausências nas features.
- Grupos numéricos: 24 contínuas e 9 indicadores binários com valores 0/1.
- Criadas duas variantes de pré-processamento sem estimador de modelo: RobustScaler nas contínuas para modelos sensíveis à escala e imputação sem escala para árvores; ambas usam imputação categórica e one-hot esparso com handle_unknown=ignore.
- Em cinco folds internos do treino, as matrizes das duas variantes foram finitas e esparsas, com cobertura completa dos holdouts. A largura variou de 193 a 199 colunas segundo as categorias presentes em cada ajuste.
- Ajustando no treino completo e transformando a validação, as duas variantes geraram 202 colunas. A validação apresentou 9 níveis inéditos em 3 features categóricas, aceitos pelo encoder sem erro.
- df_modeling_features permaneceu inalterado. O arquivo df_test_raw.csv foi conferido apenas por existência e tamanho (11.634.013 bytes); nenhum modelo ou MAPE foi calculado.
- Versões: pandas 2.3.3, NumPy 2.2.6, scikit-learn 1.7.2.
- Gate da etapa permanece pendente; a Etapa 07 não começou.
