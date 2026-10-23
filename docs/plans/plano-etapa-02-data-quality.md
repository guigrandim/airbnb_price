# Plano — Etapa 02: Qualidade e limpeza dos dados

## Objetivo

Auditar a qualidade do snapshot, decidir tratamentos rastreáveis e preparar uma única tabela de modelagem em memória, com uma linha por anúncio, para a Etapa 03.

## Escopo e premissas

- Usar `listings_details.csv` como base principal e manter os arquivos brutos imutáveis.
- Identificar nomes reais de arquivos e colunas antes de qualquer junção; validar chaves e granularidade das bases auxiliares.
- Manter features com menos de 30% de ausências, contando campos vazios e marcadores `N/A`.
- Trabalhar com anúncios de Amsterdam, conforme a decisão do usuário, e não juntar linhas diárias do calendário à tabela de modelagem.
- O usuário solicitou excluir linhas com ausências nas features selecionadas. Essa decisão substitui, para a tabela final, a proposta anterior de imputar esses valores. O impacto em linhas e a taxa de retenção precisam ser medidos antes de fechar a limpeza.
- Excluir os anúncios `20597844` e `21423332`, ambos com `price = 0`, da base de modelagem, conforme decisão do usuário; manter os registros apenas no bruto imutável e no registro de exclusões.
- O usuário autorizou a exclusão de valores identificados como erro, desde que a regra e o fallback sejam registrados em Markdown. Valores extremos não serão removidos apenas por ultrapassarem o critério de IQR.
- A tabela final deve permanecer em memória; não gerar CSV.

## Estratégia e verificações executadas

1. Auditar dimensões, tipos, chaves, duplicatas e ausências da base principal e das fontes auxiliares.
2. Resumir variáveis numéricas e categóricas, incluindo faixas, cardinalidade, assimetria e curtose.
2a. Incluir coeficiente de variação na tabela numérica, registrando a fórmula e quando a medida não é interpretável.
2b. Investigar a cauda de `bathrooms` e a frequência/consistência de `maximum_nights` para avaliar possíveis erros ou valores padrão, sem classificar valores repetidos como defaults sem evidência.
3. Conferir valores de preço, notas, datas, booleanos e disponibilidade; verificar nomes reais de campos.
4. Validar o calendário e as avaliações sem confundir indisponibilidade com reserva nem usar preços futuros como preditores.
5. Registrar regras preliminares de retenção de features, preço zero, particionamento e prevenção de vazamento.
6. Antes de encerrar a etapa, documentar a filtragem geográfica, excluir as linhas incompletas da matriz selecionada, investigar preços extremos e montar o DataFrame final em memória.

## Células registradas e execução

O notebook contém as verificações `02.1` a `02.10`, executadas em blocos via MCP Jupyter:

- `02.1 — Estrutura, tipos e ausências`
- `02.2 — Faixas, notas, datas e booleanos`, incluindo estatísticas numéricas e categóricas
- Na estatística numérica: CV amostral, skew e curtose; investigação da cauda de `bathrooms` e frequência/consistência de `maximum_nights`.
- `02.3 — Formatos e consistência de chaves`
- `02.4 — Calendário: chaves, datas e disponibilidade`
- `02.5 — Avaliações e granularidade`
- `02.6 — Plano de tratamento e partição`
- `02.7 — Resumo da auditoria inicial`

Blocos acrescentados:

- `02.8 — Escopo geográfico e seleção preliminar`: comparar bairros geocodificados com `neighbourhoods.csv` e GeoJSON; selecionar 18 features.
- `02.9 — Limpeza e seleção de linhas`: remover preços zero, os três erros de `bathrooms` e linhas incompletas; documentar o anúncio `11040717` excluído por ausências.
- `02.10 — Dataset final em memória`: montar `df_modeling_final`, associar partições anteriores à limpeza e validar estrutura; nenhum CSV foi exportado.

## Evidências já registradas no notebook

- Base principal: 20.030 anúncios, 96 colunas e IDs únicos; 54 colunas apresentam ausências.
- `price`: 20.028 valores positivos e 2 zeros; intervalo positivo de €8 a €8.500.
- Nota geral observada entre 20 e 100; notas detalhadas entre 2 e 10.
- `availability_365` está entre 0 e 365 e representa noites disponíveis, não ocupação nem noites vendidas.
- Os 20.030 anúncios correspondem aos 22 bairros do CSV e GeoJSON; nenhum foi removido por localização. Os 49 registros com `market` vazio ou diferente de Amsterdam também têm bairro oficial.
- As 17 features originais e `maximum_nights` têm menos de 30% de ausências; o conjunto final contém 18 features.
- A tabela final em memória tem 17.368 linhas e 21 colunas. Não há ausências, IDs duplicados, preços não positivos, bairros fora do escopo, `bathrooms >= 10` ou IDs sem partição.
- O DataFrame foi montado com pandas 2.3.3; `df_modeling_final` permanece apenas no kernel, sem exportação.
- Partições após a limpeza: 12.187 treino, 2.619 validação e 2.562 teste; divisão determinística sobre os 20.030 IDs originais, semente 42.
- A partição inicial por `id`, semente 42, cobriu a base integral: 14.021 treino, 3.004 validação e 3.005 teste; os anúncios retidos mantêm esses rótulos.
- A auditoria de avaliações registrou 431.830 linhas e divergências entre `number_of_reviews` e as bases detalhadas para 111 anúncios; 18 anúncios com contagem positiva não tinham linhas correspondentes nas bases auditadas.

## Decisão sobre preço extremo

O usuário decidiu não classificar `11040717` (`price=€2.500`) como erro de preço, apesar da coincidência com `monthly_price=€2.500` e `weekly_price=€1.000`. O anúncio foi excluído da tabela final somente porque faltam `reviews_per_month` e `review_scores_rating`, conforme a decisão posterior de remover linhas incompletas. O arquivo bruto preserva o registro.

## Outros valores extremos examinados

- `bathrooms` tem três registros com valor igual ou superior a 10: IDs `15199899` (100,5), `16698560` (15) e `17245735` (10). Os três descrevem imóveis inteiros com 1 quarto e capacidade para 4 hóspedes. Os valores são incompatíveis com os demais atributos observados e devem ser tratados como erros de preenchimento na tabela de modelagem; excluir os três anúncios e registrar IDs, regra e contagem no Markdown do notebook. Os dados brutos permanecem intactos.
- A tabela numérica agora inclui CV amostral (`desvio padrão / média × 100`), exibido apenas para média positiva e variáveis diferentes de latitude/longitude. `bathrooms`: CV 69,78%, skew 98,64 e curtose excedente 12.264,44; removendo provisoriamente os três valores `>=10`, o skew cai a 4,23 em 20.017 observações.
- Há 22 anúncios com `bathrooms=0`, incluindo quartos privados/compartilhados, apartamentos, barcos e outros tipos. Não foi encontrada evidência suficiente para tratar o zero como marcador de ausência; não excluir automaticamente esses registros.
- Os dois valores de `minimum_nights` acima de 365 são 999 e 1.001. Ambos respeitam `maximum_nights=1.125`; tratar como restrições incomuns de estadia longa e mantê-los, sem classificá-los como erro de digitação.
- `maximum_nights`: 1.125 aparece em 10.229/20.030 anúncios (51,07%); 10.783 anúncios excedem 365, e há 29 valores distintos acima de 365. A mediana e Q3 são 1.125; um anúncio (`7447773`) tem 9.999, além de cinco com 1.825. Não há conflitos `minimum_nights > maximum_nights`. O dicionário Inside Airbnb define o campo como máximo de noites por anúncio e avisa que regras do calendário podem diferir; a documentação consultada não confirma 1.125/9.999 como defaults. Manter valores e linhas; avaliar o campo como configuração discreta/categórica na Etapa 03, sem interpretar média/desvio isoladamente.

## Critérios de aceite

- Critério de inclusão de anúncios em Amsterdam documentado; 20.030 mapeados em bairros oficiais e zero fora do escopo.
- Lista final de 18 features registrada; todas obedecem ao limite estrito de menos de 30% de ausências.
- 2.657 linhas incompletas removidas depois das regras de preço e `bathrooms`; 17.368 linhas retidas.
- Os dois alvos zero excluídos; os três registros de `bathrooms` excluídos com IDs e justificativa; `11040717` excluído apenas por duas features ausentes.
- Restrições altas de `minimum_nights` mantidas como configurações de estadia longa; zeros em `bathrooms` não convertidos em ausências sem evidência.
- Um único DataFrame em memória, uma linha por `id`, alvo válido para a métrica escolhida e partições rastreáveis.
- Arquivos brutos preservados; nenhum CSV final criado.
- Interpretação, pendências e decisão submetidas ao gate da Etapa 02 antes de avançar.

## Status e bloqueios

- **Status:** limpeza e dataset final concluídos no notebook; gate da Etapa 02 aguarda aprovação explícita.
- **Última etapa aprovada:** Etapa 01.
- O MCP Jupyter disponibilizou leitura, edição, inserção, execução e remoção de células. O fluxo foi validado com uma célula temporária comentada, executada e removida.
- `maximum_nights=1.125` ocorre em 51,07% dos registros e não é removido; a documentação consultada não confirma que seja default. Na Etapa 03, avaliar codificação discreta/categórica.
- Não iniciar a Etapa 03 antes da aprovação do gate. A URL de origem foi dispensada pelo usuário.

Notebook de referência: [price_prediction.ipynb](../../notebooks/price_prediction.ipynb).

## Revisão solicitada antes do gate: partição e limpeza por conjunto

- **Objetivo:** definir treino/validação/teste logo no início do Data Quality e aplicar os mesmos critérios de limpeza a cada conjunto.
- **Escopo:** manter a divisão 70/15/15 por `id`, semente 42; aplicar em cada partição o escopo geográfico já aprovado, conversão do preço, exclusão de preços não positivos, remoção de `bathrooms >= 10` e casos incompletos nas colunas selecionadas. Preservar os rótulos de partição na tabela final em memória.
- **Estratégia:** criar `02.0` para particionar todos os IDs originais antes de `02.1`; na limpeza, separar as linhas usando o mapa inicial e chamar uma função documentada uma vez para treino, validação e teste; concatenar os resultados e consolidar as auditorias de exclusão. A célula `02.10` somente validará o resultado, sem sortear novamente.
- **Premissas:** os IDs do snapshot são únicos e não nulos; as regras de limpeza permanecem as já registradas; o pedido atual do usuário autoriza a função de limpeza na célula do notebook, como exceção à regra geral contra funções próprias.
- **Células previstas:** inserir Markdown e código `02.0`; atualizar a descrição de `02.6`; ajustar `02.9` para limpar cada partição pela função aprovada; substituir o re-sorteio em `02.10` por validações.
- **Critérios de aceite:** partição cobre os 20.030 IDs, sem sobreposição, com 14.021/3.004/3.005 IDs; cada conjunto passa pela mesma função; totais finais permanecem consistentes com a limpeza registrada; `df_modeling_final` mantém 17.368 linhas e as partições esperadas, sem exportar CSV; Etapa 03 continua bloqueada até aprovação da Etapa 02.
- **Status:** desenho aprovado pelo usuário; implementação em andamento. A execução do notebook confirmará as contagens antes da atualização deste status.

## Revisão 2 — teste bruto preservado para avaliação

Esta decisão substitui a proposta anterior de aplicar uma função de limpeza às três partições.

- **Objetivo:** preservar a partição de teste sem limpeza até a avaliação do modelo, reduzindo risco de vazamento durante exploração, engenharia e seleção.
- **Escopo aprovado:** manter divisão 70/15/15 por `id` e semente 42 no início do Data Quality; salvar as linhas originais do teste, com todas as colunas e valores textuais, em `data/processed/df_test_raw.csv`; limpar somente treino e validação para a base de desenvolvimento em memória.
- **Avaliação futura:** após congelar o modelo e as regras aprendidas no desenvolvimento, carregar o CSV bruto do teste e aplicar nele as regras já definidas, sem reajustar transformações com base no teste. Não treinar, selecionar features ou ajustar parâmetros com o teste.
- **Artefato:** `df_test` no kernel e `data/processed/df_test_raw.csv` em disco; a tabela de desenvolvimento limpa permanece em memória.
- **Limitação de independência:** antes desta solicitação, a Etapa 02 já havia inspecionado distribuições e definido filtros usando o snapshot completo. O arquivo de teste será mantido intocado a partir desta revisão, mas não se pode afirmar independência histórica total das decisões de Data Quality já tomadas.
- **Células previstas:** manter `02.0` para partição e persistência bruta do teste; ajustar `02.9` para limpar apenas treino/validação; ajustar `02.10` para validar a base de desenvolvimento e a integridade/localização do teste bruto.
- **Critérios de aceite:** teste salvo com 3.005 IDs, 96 colunas, todos associados à partição teste; arquivo bruto presente; nenhuma regra de limpeza executada no `df_test`; base limpa em memória contém somente treino e validação; não treinar nem avaliar modelos nesta revisão; Etapa 03 aguarda aprovação da Etapa 02.
- **Status:** desenho aprovado pelo usuário; implementação em andamento.

## Evidências da revisão 2 e estado atual

- A célula `02.0` executou primeiro a partição: 20.030 IDs, sem ausências ou duplicatas; 14.021 treino, 3.004 validação e 3.005 teste; sobreposição `False` e cobertura completa `True`.
- `df_test` foi criado antes da limpeza com 3.005 linhas e 96 colunas, todas como texto, e salvo em `data/processed/df_test_raw.csv` (11.634.013 bytes). A validação confirmou IDs de teste corretos, esquema preservado, nenhuma coluna de partição adicionada e arquivo presente.
- `02.6` apenas revalida a partição inicial; não há segundo sorteio.
- A limpeza de `02.9` processou 17.025 linhas de treino e validação: removeu 2 preços zero, 3 erros de `bathrooms >= 10` e 2.214 linhas incompletas. `df_modeling_final` tem 14.806 linhas por 21 colunas: 12.187 treino e 2.619 validação.
- A validação de `02.10` não encontrou IDs duplicados, ausências, preços não positivos, bairros fora do escopo, `bathrooms >= 10` ou partições inválidas. O teste bruto não foi limpo e não foi incluído na tabela de desenvolvimento.
- O pedido anterior de função de limpeza para as três partições foi substituído pelo pedido de preservar o teste bruto e limpar apenas na avaliação. Não foi criada função própria no notebook.
- O `.gitignore` cobre `/data/`; portanto, `df_test_raw.csv` foi salvo localmente, mas não aparece no versionamento. Não foi alterada essa regra.
- **Status:** revisão implementada no notebook e saída inspecionada; gate da Etapa 02 ainda aguarda aprovação explícita. Última etapa aprovada: Etapa 01. Não iniciar a Etapa 03.

## Controle da revisão vigente

A proposta intermediária de limpar as três partições com uma função foi supersedida pela Revisão 2 e não deve ser executada. As contagens de 17.368 linhas e 2.657 casos incompletos documentadas na versão anterior descrevem o conjunto antes da reserva do teste; o resultado vigente para a base limpa de desenvolvimento é 14.806 linhas, com o teste bruto mantido em arquivo separado. A Revisão 2 está implementada e inspecionada; permanece pendente somente a aprovação explícita do gate da Etapa 02.

## Revisão 3 — viabilidade de acrescentar dados auxiliares

- **Objetivo:** verificar quais fontes em `data/raw` podem acrescentar atributos úteis a `df_modeling_final` sem alterar sua granularidade de uma linha por anúncio.
- **Escopo desta revisão:** a inspeção inicial avaliou esquemas, chaves e granularidades. Após autorização explícita do usuário, foi integrada ao desenvolvimento uma agregação de `reviews.csv`. `calendar.csv` permanece excluído.
- **`listings.csv`:** 20.030 IDs únicos, sem IDs ausentes ou divergentes frente à base detalhada. Seus 16 campos são uma visão resumida e se sobrepõem em grande parte aos de `listings_details.csv`; `neighbourhood_group` está vazio em todos os 20.030 registros. Não há ganho identificado em juntar essa tabela.
- **`neighbourhoods.csv`:** 22 nomes de bairro, sem duplicidade indicada pela auditoria; `neighbourhood_group` está vazio nas 22 linhas. `neighbourhood_cleansed` já está em `df_modeling_final`; esta tabela não oferece coluna categórica preenchida para acrescentar.
- **`reviews.csv`:** 431.830 linhas com `listing_id` e `date`; a auditoria encontrou zero IDs de anúncio órfãos. É possível agregar por anúncio e juntar à base por `id` após a agregação, preservando uma linha por anúncio. Candidatas: quantidade de avaliações no intervalo móvel de 365 dias até 06/12/2018 e dias desde a avaliação mais recente até essa data.
- **`reviews_details.csv`:** contém os mesmos 431.830 eventos, com os mesmos pares `listing_id` + `date`, e acrescenta identificadores pessoais e comentários. Não oferece eventos adicionais para a agregação; não é recomendada para esta integração.
- **`neighbourhoods.geojson`:** contém geometrias dos 22 bairros e pode apoiar uma derivação geográfica em etapa própria; não é uma junção tabular que acrescente uma coluna útil diretamente nesta revisão.
- **`calendar.csv`:** deliberadamente excluído, conforme orientação do usuário. Não agregar suas 365 linhas por anúncio nesta alteração.
- **Qualidade e limitação dos reviews:** a auditoria anterior do snapshot completo encontrou 111 divergências entre 17.624 anúncios comparáveis e 18 anúncios com contagem positiva sem linhas nos arquivos de avaliações. Na execução autorizada, entre os 14.806 anúncios de desenvolvimento, foram encontradas 91 divergências e nenhum anúncio com contagem positiva sem eventos. A contagem original foi mantida e não foi sobrescrita.
- **Candidatas da base principal fora do DataFrame:** `last_review` (12,01% ausentes no snapshot) e `calculated_host_listings_count` já existem em `listings_details.csv`; podem ser avaliadas sem join externo. `last_review` pode fornecer recência de avaliação, mas precisa de regra explícita para ausências e corte no snapshot.
- **Resultado da integração:** `reviews.csv` foi agregado por `listing_id` e unido por `id` somente ao desenvolvimento. A junção acrescentou `reviews_last_365d` e `days_since_last_review`, preservando uma linha por anúncio e todos os IDs/partições. `listings.csv` e `neighbourhoods.csv` não foram unidos; `reviews_details.csv` não oferece eventos adicionais; `calendar.csv` foi excluído.
- **Impacto observado:** nenhuma linha foi adicionada ou removida pela junção; a tabela final passou de 21 para 23 colunas. Não há resultado de MAPE nesta etapa.
- **Células executadas:** `02.9.2` leu `listing_id` e `date` de `reviews.csv` e conferiu cobertura; `02.9.3` agregou e juntou as métricas com validação um-para-um; `02.10` confirmou linhas, IDs, partições, ausência de nulos nas métricas e integridade do teste.
- **Tratamento aplicado:** corte temporal fixo em 06/12/2018; `reviews_last_365d` conta eventos na janela móvel encerrada no snapshot; `days_since_last_review` mede dias desde a última avaliação. A contagem da janela foi preenchida com zero para 3.557 anúncios sem eventos recentes porque todos os anúncios de desenvolvimento têm histórico na fonte. Não houve ausência temporal na data da última avaliação.
- **Critérios de aceite:** a tabela agregada tem no máximo uma linha por `listing_id`; a junção à base de desenvolvimento é um-para-um; o total permanece 14.806 linhas e os IDs/partições não mudam; a saída lista divergências e ausências; nenhum filtro ou transformação é aplicado a `df_test` ou `df_test_raw.csv`.
- **Estado:** integração autorizada, executada no notebook em blocos MCP e inspecionada; evidências finais e decisão do gate constam na seção seguinte.

## Execução da Revisão 3 — integração implementada e inspecionada

- `02.9.2` leu `listing_id` e `date` de `reviews.csv`, restringiu as métricas aos IDs de treino e validação e aplicou o corte temporal de 06/12/2018. Foram associados 371.840 eventos; os 14.806 anúncios de desenvolvimento têm histórico na fonte. Datas inválidas: 0; eventos após o snapshot: 0.
- Foram criadas duas métricas por anúncio: `reviews_last_365d`, contagem na janela móvel de 365 dias encerrada no snapshot, e `days_since_last_review`, dias desde o último evento até o snapshot. A tabela agregada tem 14.806 linhas e nenhum ID duplicado.
- `02.9.3` juntou as métricas por `id` com validação um-para-um. Linhas, IDs, ordem e partições foram preservados; anúncios sem correspondência: 0; ausências nas duas métricas: 0; `df_modeling_pre_split` permaneceu inalterado.
- Em 3.557 anúncios não houve avaliação dentro da janela móvel; a contagem foi definida como zero porque todos possuem histórico na fonte. `reviews_last_365d`: mínimo 0, mediana 4, máximo 166. `days_since_last_review`: mínimo 0, mediana 101, máximo 2.584.
- A contagem de eventos da fonte diverge de `number_of_reviews` em 91 anúncios de desenvolvimento. Nenhum anúncio com contagem positiva na coluna original ficou sem evento na fonte. `number_of_reviews` foi mantida sem substituição; as diferenças ficam registradas como limitação de consistência entre fontes. O diagnóstico anterior de 111 divergências e 18 anúncios sem eventos refere-se à auditoria de cobertura do snapshot completo, antes da separação de desenvolvimento e teste.
- A célula `02.10` foi executada novamente. `df_modeling_final` tem 14.806 linhas × 23 colunas: `id`, `price`, 20 preditoras (18 da base principal e as duas métricas agregadas) e `particao`. A divisão é 12.187 treino e 2.619 validação. IDs duplicados, ausências nas preditoras/alvo, preços não positivos, bairros fora do escopo, `bathrooms >= 10` e IDs sem partição: 0.
- `df_test` continua com 3.005 linhas × 96 colunas textuais, sem alteração de esquema, sem coluna de partição e sem agregação/limpeza; `data/processed/df_test_raw.csv` permanece presente com 11.634.013 bytes.
- `listings.csv` e `neighbourhoods.csv` não acrescentam campos preenchidos úteis à base; `reviews_details.csv` contém os mesmos eventos e adiciona comentários/dados pessoais. `calendar.csv` foi excluído conforme pedido. Não foram criados arquivos CSV para a base final de modelagem.
- **Status:** integração de `reviews.csv` e validação da base final executadas e inspecionadas. O usuário aprovou o gate revisado ao solicitar a implementação da Etapa 03; a última etapa aprovada é a Etapa 02. A base de desenvolvimento permanece em memória e o teste bruto reservado.
