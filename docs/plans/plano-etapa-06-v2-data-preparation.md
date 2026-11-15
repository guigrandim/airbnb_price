# Etapa 06 V2 — Preparação dos dados

Data 15/11/2026. Etapa06V2 aprovada pelo usuário e Etapa07V2 autorizada. Preparação implementada, executada e salva após reconexão do MCP.

## Objetivo

Preparar transformações reproduzíveis para as 36 features aprovadas, com 14.018 anúncios de treino e 3.003 de validação.

## Estratégia e premissas

- Confirmar objetos do kernel, exclusão ID20644162, IDs disjuntos, preço positivo e esquema aprovado.
- Usar27numéricas e9categóricas. Separar indicadores explícitos has_review_history,rating_missing,review_rate_missing,is_studio de contínuas.
- Numéricas contínuas recebem mediana. Variante para árvores dispensa escala. Variante sensível à escala usa RobustScaler pela cauda observada na EDA. Indicadores binários preservam0/1.
- MissingIndicator(features=all) para contínuas e categóricas preserva ausência inclusive quando surgir apenas na validação. Indicadores mantêm0/1 em ramos separados da escala e largura fixa. Algumas colunas serão constantes no treino, decisão consciente pelo contrato estável.
- Categóricas recebem imputação pela moda e OneHotEncoder(handle_unknown=ignore,sparse_output=True). Normalizar pd.NA para np.nan em cópias antes dos pipelines.
- Definir templates não ajustados. Verificar clones em3folds de treino, fit apenas no fold de ajuste, nomes únicos, finitude, linhas e estatísticas de imputação.
- Auditar clones ajustados no treino completo e transform na validação. Registrar níveis desconhecidos, nomes de saída, matriz e caso sintético com ausências e categoria inédita.
- Os templates permanecem disponíveis para encaixar em pipelines de estimadores na Etapa07. As cópias ajustadas servem à auditoria.
- Dados/modelos apenas em memória. Conferir hash do teste congelado, sem ler registros. Sem treinamento de regressor nesta etapa.

## Células previstas

1. Entrada, normalização de nulos e grupos.
2. Templates de preparação com e sem escala.
3. Verificação por folds e estatísticas de treino.
4. Auditoria da validação, categorias inéditas e caso sintético.
5. Conclusões, versões, integridade e gate.

## Critérios de aceite

- As36colunas cobrem apenas as features aprovadas e preservam nulos para aprendizado nos folds.
- Imputadores, encoder e escala aprendem somente no treino de ajuste.
- Matrizes finitas, linhas preservadas e nomes únicos. Desconhecidos e novas ausências aceitos.
- Templates não ajustados e clones de auditoria identificados.
- Base e teste preservados. Plano atualizado e aprovação solicitada antes de07V2.

## Evidências e gate

- A aprovação da Etapa05V2 foi registrada no plano correspondente.
- A leitura da célula final da Etapa05 pelo MCP retornou erro de conteúdo. Inserção da seção06 e abertura do notebook pelo MCP expiraram.
- Inspeção do arquivo em disco confirmou 273 células, terminando na auditoria05V2. A seção06 não foi inserida.
- Processos de JupyterLab, kernel e MCP estão ativos. Isso confirma processos locais, mas não valida comunicação com o frontend ou estado atual dos objetos do kernel.
- Usuário solicitado a abrir ou recarregar a aba do JupyterLab com o notebook. Retomar pela leitura MCP e uma célula simples de verificação do ambiente.
- Registro acima descreve a interrupção inicial. Após confirmação do usuário, o MCP voltou a responder e as células273–281 foram inseridas e executadas. Kernel Python3.10.4 com objetosV2 disponíveis.
- Entrada confirmada com14.018linhas de treino,3.003de validação e36features. Separação23contínuas/4binárias/9categóricas. ID20644162 ausente e partições disjuntas.
- Templates `v206_tree_preprocessor` e `v206_scaled_preprocessor` definidos sem ajuste. Cópias de auditoria em `v206_audit_preprocessors`.32indicadores explícitos de ausência ficam separados da escala, com largura fixa.
- Três folds internos verificaram6transformações. Larguras127,126,128colunas nas duas variantes, saída esparsa, valores finitos e nomes únicos. Medianas coincidiram com os dados de ajuste de cada fold e centros da escala foram conferidos. Cada linha de treino ficou exatamente uma vez no holdout.
- Ajuste no treino completo produziu130colunas nas duas variantes, com esquema idêntico. Validação3003linhas recebeu transform. Dois níveis inéditos de property_type em duas linhas foram aceitos pelo encoder.
- Três casos sintéticos por variante verificaram categorias novas,23contínuas ausentes e9categóricas ausentes. Os indicadores marcaram as ausências e estatísticas de imputação permaneceram iguais após transform.
- FonteV2 preservada e hash do teste conferido. pandas2.3.3,numpy2.2.6,scikit-learn1.7.2. Etapa07V2 aguarda gate06V2.
- O AGENTS.md exige edição e execução por MCP funcional e determina registrar o impedimento quando a conexão falha.

## Conclusão e gate

Etapa implementada, executada e salva pelo MCP. A auditoria final confirmou36entradas,130saídas,6checks de folds e2auditorias de validação.18dos32indicadores de ausência são constantes em zero no treino, custo aceito para manter largura fixa e suportar ausências novas. Os templates continuam sem fit, com clones ajustados identificados para auditoria.

O comando específico de salvar notebook encontrou estado de diálogo. O comando padrão `docmanager:save` salvou as células e as saídas. A janela foi consultada pela skill computer-use para diagnóstico, sem edição de células pela interface. A revisão estática do subagente conferiu273–281 sem encontrar bug concreto de fit/transform, escala ou indicadores.

Gate06V2 aguarda aprovação. Última etapa aprovada05V2. Próxima etapa07V2 depende desse gate.
