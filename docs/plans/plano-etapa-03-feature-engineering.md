# Plano de implementação — Etapa 03: Feature Engineering

**Objetivo:** criar atributos interpretáveis sobre capacidade, localização, anfitrião, reputação e regras de estadia que possam melhorar a previsão do preço anunciado em Amsterdam.

**Arquitetura:** partir da base limpa de desenvolvimento em memória, preservar as colunas originais e gerar um novo objeto `df_modeling_features`. A engenharia determinística será aplicada a treino e validação; parâmetros ou cortes aprendidos serão ajustados somente no treino. O teste permanecerá bruto em `data/processed/df_test_raw.csv` até a avaliação final.

**Tecnologias previstas:** Python, pandas e NumPy já usados no notebook; Jupyter MCP para ler, editar, executar e inspecionar as células.

**Referências do projeto:** `AGENTS.md`; `notebooks/price_prediction.ipynb`; plano da Etapa 02 em `docs/plans/plano-etapa-02-data-quality.md`.

**Status:** plano mantido na versão anterior solicitada pelo usuário e atualizado para refletir a entrada revisada da Etapa 02. O usuário autorizou a implementação. As células da Etapa 03 foram executadas e inspecionadas via MCP Jupyter; o gate da Etapa 03 aguarda aprovação.

---

## 1. Contexto confirmado pela nova execução

A célula `02.10`, executada após a integração de avaliações, confirma `df_modeling_final` com **14.806 linhas e 23 colunas**: `id`, `price`, 20 features e `particao`. As 20 features incluem 18 campos da base principal e `reviews_last_365d` e `days_since_last_review`, agregados de `reviews.csv` por anúncio até 06/12/2018. Há 12.187 anúncios de treino e 2.619 de validação. A partição original de 20.030 IDs tem 14.021 em treino, 3.004 em validação e 3.005 em teste. O teste foi separado em `df_test`, com 3.005 linhas e 96 colunas brutas, salvo em `data/processed/df_test_raw.csv`.

O contrato da Etapa 03 é `df_modeling_final`, a base limpa de desenvolvimento confirmada na última execução do notebook. Ela contém apenas treino e validação; o teste segue reservado em sua forma bruta.

A execução de `02.10` confirma 0 IDs duplicados, 0 células ausentes nas features e no alvo, 0 preços não positivos e 0 anúncios fora dos bairros oficiais na base de desenvolvimento. O preço nela vai de €8 a €8.500, com mediana de €125. A integração de avaliações foi validada sem alterar linhas, IDs ou partições.

**Limitação de independência:** a auditoria e algumas decisões de Data Quality anteriores à reserva do teste consultaram o snapshot completo. A partir da revisão da Etapa 02, o arquivo do teste fica reservado e não será usado para criar ou selecionar features; ainda assim, a independência histórica absoluta das decisões anteriores não pode ser afirmada.

### Colunas confirmadas na base de desenvolvimento

`id`, `price`, `room_type`, `property_type`, `accommodates`, `bedrooms`, `bathrooms`, `neighbourhood_cleansed`, `latitude`, `longitude`, `host_is_superhost`, `host_since`, `host_listings_count`, `number_of_reviews`, `reviews_per_month`, `review_scores_rating`, `minimum_nights`, `maximum_nights`, `availability_365`, `instant_bookable`, `reviews_last_365d`, `days_since_last_review`, `particao`.

O alvo é `price` em euros. `id` identifica o anúncio e `particao` indica treino/validação; ambos ficam fora da matriz de preditores. A coluna real de nota geral é `review_scores_rating`, com escala observada de 20 a 100 no snapshot. `availability_365` representa noites disponíveis no calendário, não noites ocupadas ou vendidas.

## 2. Escopo

### Incluído

- Gerar atributos derivados das 20 features confirmadas, com nomes, fórmulas, justificativa de negócio e ressalvas registrados neste plano e no dicionário de features do notebook. As duas métricas agregadas de avaliações já fazem parte da entrada e não serão recalculadas nesta etapa.
- Manter `df_modeling_final` como fonte imutável da Etapa 02 e criar `df_modeling_features` para os atributos da Etapa 03.
- Usar somente treino para qualquer estatística, centro geográfico, agrupamento por frequência, associação entre preditores ou corte aprendido dos dados. Aplicar a mesma regra à validação, sem refazer o ajuste.
- Executar verificações curtas depois de cada bloco de 1–3 células MCP e inspecionar as saídas antes de continuar.
- Preservar a partição e os IDs; manter o teste bruto sem leitura ou transformação nesta etapa.

### Fora do escopo

- Treinar modelos, calcular MAPE ou afirmar que uma feature melhora desempenho. Isso será medido com comparações controladas nas etapas de modelagem, usando validação e mantendo o teste reservado.
- Escalonamento, imputação, one-hot encoding e tratamento de categorias desconhecidas; pertencem à Etapa 06 e devem ficar em `Pipeline`/`ColumnTransformer`.
- Feature selection supervisionada; pertence à Etapa 05 e deve usar somente treino/CV.
- Usar `calendar.csv` como fonte de preços futuros, tratar disponibilidade como ocupação, ou juntar avaliações futuras.
- Criar atributos derivados de `price`, como preço por hóspede, ou codificação/estatística de categorias calculada com o alvo.
- Definir funções, classes ou lambdas no notebook. A implementação seguirá o fluxo sequencial auditável especificado em `AGENTS.md`.

## 3. Catálogo proposto de features

As propostas são hipóteses de engenharia, não ganhos garantidos. As colunas-base permanecem disponíveis para comparação; o conjunto final só será congelado depois dos gates posteriores.

| Grupo | Feature candidata | Fórmula ou regra | Hipótese de negócio e controle |
|---|---|---|---|
| Capacidade | `is_studio` | `bedrooms == 0` | Distingue anúncios sem quarto separado; validar a interpretação junto de `room_type` e `property_type`, pois zero quarto sozinho não comprova que o imóvel seja um estúdio. |
| Capacidade | `bedrooms_per_guest` | `bedrooms / accommodates`, somente quando `accommodates > 0` | Representa quartos relativos à capacidade, ajudando a separar imóveis de mesma lotação com configurações distintas. |
| Capacidade | `bathrooms_per_guest` | `bathrooms / accommodates`, somente quando `accommodates > 0` | Representa disponibilidade de banheiros por hóspede; manter zeros de `bathrooms` como valores observados conforme decisão da Etapa 02. |
| Capacidade | `accommodates_log1p` — opcional | `log1p(accommodates)` | Candidato para modelos sensíveis à escala e à relação não linear; manter o original e comparar por ablação. Árvores podem não se beneficiar. |
| Anfitrião | `host_tenure_years` | `(2018-12-06 - host_since).days / 365.25` | Experiência acumulada até a data do snapshot, sem usar a data atual. Datas posteriores ao snapshot devem ser auditadas, não convertidas silenciosamente em tenure zero. |
| Anfitrião | `host_listings_log1p` | `log1p(host_listings_count)` para valores não negativos | Reduz a influência da cauda de portfólios grandes; manter a contagem original para comparação. |
| Anfitrião | `host_has_multiple_listings` | `host_listings_count > 1` | Distingue anfitriões com mais de um anúncio; não classifica automaticamente anfitriões como profissionais. |
| Reputação | `number_of_reviews_log1p` | `log1p(number_of_reviews)` para valores não negativos | Representa volume de avaliações com escala menos dominada por contagens altas. Não interpretar como reservas recentes. |
| Reputação | `reviews_per_month_log1p` | `log1p(reviews_per_month)` para valores não negativos | Representa ritmo observado de avaliações; não equivale a ocupação e pode refletir tempo ativo do anúncio. |
| Reputação | `is_superhost` | Mapear `t` → 1 e `f` → 0 após validar os valores observados | Padroniza o booleano para algoritmos que usam atributos numéricos; preservar a coluna original para auditoria. |
| Reputação | `is_instant_bookable` | Mapear `t` → 1 e `f` → 0 após validar os valores observados | Representa reserva instantânea; manter a codificação categórica original disponível para comparação no preparo. |
| Interação | `rating_x_superhost` — opcional | `review_scores_rating × is_superhost`, com nota na escala observada de 20–100 | Permite relação distinta entre nota e preço para superhosts; medir redundância no treino e testar contribuição apenas nas etapas de modelagem. |
| Localização/segmento | `room_type_neighbourhood` — opcional | Combinação textual estável de `room_type` e `neighbourhood_cleansed` | Permite padrões específicos de quarto por bairro. Os 22 bairros oficiais foram confirmados no snapshot; medir cardinalidade e frequência das combinações somente no treino. Não usar target encoding nesta etapa. |
| Localização/segmento | `property_type_room_type` — opcional | Combinação textual estável de `property_type` e `room_type` | Captura configurações como tipo de propriedade dentro da categoria de quarto. Medir cardinalidade e frequência no treino; descartar se gerar esparsidade excessiva. |
| Disponibilidade | `availability_full_year` — opcional | `availability_365 == 365` | Identifica anúncios disponíveis todos os dias do calendário observado; não significa ocupação ou capacidade vendida. |
| Disponibilidade | `availability_low` — opcional | `availability_365 <= 30` | Identifica disponibilidade baixa no snapshot. A mediana observada no snapshot é 3 dias; o corte de 30 é uma hipótese operacional, não uma regra legal ou uma medida de reservas. |
| Restrição de estadia | `minimum_nights_log1p` | `log1p(minimum_nights)` para valores não negativos | Representa a restrição mínima com menor influência dos valores muito altos; manter `minimum_nights` original. |
| Restrição de estadia | `minimum_nights_over_30` — opcional | `minimum_nights > 30` | Sinaliza uma estadia mínima mensal ou superior; é uma faixa analítica, não uma classificação legal. |
| Restrição de estadia | `maximum_nights_log1p` — opcional | `log1p(maximum_nights)` para valores não negativos | Reduz a escala de valores altos, incluindo 9.999; manter valor e flag para avaliar representações alternativas. |
| Restrição de estadia | `maximum_nights_over_365` — opcional | `maximum_nights > 365` | Separa limites acima de um ano das restrições anuais; não significa que o anúncio aceite reservas por todo esse período. |
| Restrição de estadia | `maximum_nights_equals_1125` — exploratória | `maximum_nights == 1125` | Isola a massa observada em 1.125: 10.229 dos 20.030 anúncios do snapshot. A Etapa 02 não encontrou evidência documental de que seja um valor padrão. Avaliar como configuração discreta, sem removê-la. |
| Geoespacial | `distance_to_amsterdam_center_km` — opcional | Distância geodésica entre coordenadas e um centro oficial definido a partir do GeoJSON de bairros | Pode resumir centralidade além do bairro. Antes de implementar, confirmar CRS e definição reproduzível do centro; não adicionar dependência sem necessidade. Se o centro for estimado dos anúncios, ajustá-lo apenas no treino. |

### Prioridade de construção

1. **Primeiro bloco:** `is_studio`, `bedrooms_per_guest`, `bathrooms_per_guest`, `host_tenure_years`, `host_listings_log1p`, `host_has_multiple_listings`, `number_of_reviews_log1p` e `reviews_per_month_log1p`.
2. **Segundo bloco:** booleanos padronizados, `minimum_nights_log1p`, `maximum_nights_log1p` e os indicadores de disponibilidade/restrição. Confirmar domínio e ausências antes de gerar.
3. **Bloco exploratório:** interações de bairro/tipo de quarto e nota/superhost; medir cardinalidade e redundância no treino antes de manter como candidatas. O efeito sobre MAPE será avaliado apenas na modelagem.
4. **Geoespacial opcional:** só construir se a referência e o CRS do GeoJSON forem confirmados sem dependência desnecessária.

## 4. Regras contra vazamento e estabilidade

- Não incluir `price`, `id` ou `particao` como preditores. Não calcular agregações de preço por bairro, tipo ou anfitrião.
- Usar a data fixa do snapshot (`2018-12-06`) para tenure; nunca usar a data atual ou informação posterior.
- Preservar `df_test` e `data/processed/df_test_raw.csv` sem consulta ou transformação até a avaliação futura. Gerar suas features somente após congelar o pipeline e aplicando as regras aprendidas no desenvolvimento.
- Fórmulas determinísticas podem ser aplicadas de forma idêntica a treino e validação. Qualquer mediana, centro, quantil, limite por frequência ou agrupamento estimado dos dados deve ser ajustado somente no treino e reaplicado à validação.
- Proteger razões contra denominador zero; proteger `log1p` contra valores negativos; registrar qualquer valor inválido e não substituir por zero sem hipótese documentada.
- Não substituir colunas-base por derivadas durante a primeira comparação. Manter linhagem e poder medir ablações posteriormente.
- Codificação de categorias e escalas ficam para a Etapa 06. A seleção final fica para a Etapa 05; a eventual contribuição para MAPE será quantificada mais tarde em validação e nunca inferida só pela fórmula.
- `maximum_nights=1125` é tratado como valor observado frequente, não como default comprovado. `availability_365` continua sendo disponibilidade, não ocupação.
- A avaliação de redundância na Etapa 03 será descritiva e restrita ao treino: correlação entre explicativas numéricas, associação entre categóricas e cardinalidade das interações. Ela não usa `price` para escolher atributos nem substitui a EDA e a seleção das etapas seguintes.

## 5. Sequência prevista no notebook

As células serão inseridas e executadas em blocos pequenos pelo MCP Jupyter, com Markdown explicativo imediatamente antes/depois do código e comentários em português nas células Python.

| Seção | Conteúdo previsto | Saída/controle |
|---|---|---|
| `## Etapa 03 — Feature Engineering` | Objetivo, base de entrada, split, escopo e regra de teste reservado. | Confirmação de que nenhum modelo será treinado nesta etapa. |
| `### 03.1 — Verificação do contrato da base e prevenção de vazamento` | Conferir existência de `df_modeling_final`, nomes, dimensões, partições e referência ao teste reservado, usando o contrato observado de 14.806 × 23. | Mostrar esquema observado e interromper se o objeto não corresponder ao contrato aprovado. |
| `### 03.2 — Verificação da capacidade e configuração do imóvel` | Criar os atributos de estúdio e razões de quartos/banheiros por hóspede com guardas. | Conferir divisões, faixas, infinitos e exemplos. |
| `### 03.3 — Verificação de anfitrião e reputação` | Criar tenure pelo snapshot, logs de volume/taxa, portfólio múltiplo e booleanos validados. | Conferir domínios, datas negativas/futuras e valores inválidos. |
| `### 03.4 — Verificação da localização e interações` | Construir cruzamento bairro × tipo de quarto após medir cardinalidade; avaliar a feature geoespacial opcional somente se a referência puder ser definida. | Registrar cardinalidade, combinações raras e razão de inclusão ou descarte. |
| `### 03.5 — Verificação de restrições e disponibilidade` | Criar transformações candidatas de noites mínimas/máximas e flags de disponibilidade, respeitando a interpretação das colunas. | Conferir valores e registrar que disponibilidade não representa ocupação. |
| `### 03.6 — Verificação do dicionário, integridade e gate` | Consolidar nomes, fórmulas, tipo, fonte, hipótese e decisão de manter/adiar; criar `df_modeling_features` sem alterar a base original. | Confirmar IDs/partições, colunas originais, ausência de infinitos e teste bruto inalterado; submeter o gate da Etapa 03. |

## 6. Critérios de aceite da Etapa 03

- A base de entrada corresponde ao contrato observado na execução da Etapa 02: `df_modeling_final` com 14.806 × 23, 20 features existentes e partições de treino/validação preservadas.
- O dicionário informa, para cada feature criada, nome, fórmula, tipo, origem, hipótese de negócio, limitações e decisão de inclusão.
- `df_modeling_final` permanece inalterado; a saída é um novo objeto em memória com as mesmas linhas e rótulos de treino/validação.
- `id`, `price` e `particao` não aparecem como preditores; não há preço futuro, target encoding ou informação futura.
- Razões e logs têm tratamento explícito para denominadores zero e valores negativos; as verificações não encontram `inf`/`-inf` e toda ausência adicional fica explicada.
- Features que dependem de dados aprendidos usam somente treino para ajuste; validação recebe a mesma transformação sem `fit`.
- `df_test` e seu arquivo bruto não são limpos, inspecionados por valores de negócio ou usados para selecionar features nesta etapa.
- Nenhum ganho de MAPE é alegado nesta etapa. As features candidatas serão comparadas em validação nas etapas de modelagem/seleção, mantendo o teste fechado.
- O gate da Etapa 03 é apresentado com evidências, limitações e pendências antes de avançar para a Etapa 04.

## 7. Pendências e estado do gate

1. Base usada na Etapa 03: `df_modeling_final` (14.806 × 23), conforme execução verificada da Etapa 02; inclui duas métricas agregadas de `reviews.csv` até o snapshot.
2. O gate revisado da Etapa 02 foi aprovado pelo pedido explícito de implementar a Etapa 03.
3. A sequência de células e o dicionário foram executados em pequenos blocos pelo MCP Jupyter, mantendo o teste reservado.
4. O gate da Etapa 03 aguarda aprovação antes de qualquer trabalho da Etapa 04.

## 8. Execução, evidências e estado do gate

- A célula `03.1` confirmou a entrada com 14.806 linhas × 23 colunas, 20 preditoras, 12.187 anúncios de treino e 2.619 de validação. `df_modeling_final` foi copiado para `df_modeling_features`, sem alterar a fonte. Versões registradas: pandas 2.3.3 e NumPy 2.2.6; semente 42.
- `03.2` criou quatro features de capacidade. Não houve `accommodates <= 0`, quartos ou banheiros negativos, ausências ou infinitos. Há 806 anúncios com `bedrooms=0`; a flag `is_studio` não comprova o tipo real do imóvel.
- `03.3` criou sete features de anfitrião e reputação. Não houve `host_since` futuro/ausente, contagens negativas ou booleanos fora de `t/f`. As sete saídas não têm ausências nem infinitos.
- `03.4` mediu no treino 60 combinações de quarto × bairro (16 com menos de 20 anúncios, cobrindo 43 linhas) e 53 de propriedade × quarto (33 com menos de 20 anúncios, cobrindo 158 linhas). Criou duas interações categóricas, uma de nota/superhost e a distância geodésica em quilômetros.
- O GeoJSON tem 22 geometrias `MultiPolygon`, sem CRS declarado. A candidata `distance_to_amsterdam_center_km` baseada em centro oficial não foi criada. A feature implementada é `distance_to_training_center_km`, distância Haversine ao centro mediano calculado somente no treino (52,36471983211245; 4,88606668034429). O GeoJSON serviu para conferir limites; zero coordenadas da base de desenvolvimento ficaram fora deles. Esta distância é proxy de centralidade da amostra, não distância ao centro oficial.
- `03.5` criou sete features de restrição e disponibilidade, sem valores inválidos, ausências ou infinitos. A flag `maximum_nights_equals_1125` vale 1 para 7.398 anúncios de desenvolvimento; isso não comprova que 1.125 seja um default. `availability_low` vale 1 para 9.884 anúncios, sem indicar reservas.
- `03.6` calculou associações sem `price`, apenas no treino: 14 pares numéricos com |Spearman| ≥ 0,90 e 8 com |Pearson| ≥ 0,90. O maior Pearson foi 0,999638 entre `is_superhost` e `rating_x_superhost`. Logs, flags e interações redundantes permanecem candidatas para comparação posterior. O dicionário das 22 novas features está em duas células Markdown do notebook.
- A verificação final confirmou `df_modeling_features` com 14.806 linhas × 45 colunas: 20 preditoras originais, 22 novas features, `id`, `price` e `particao`. As 23 colunas da entrada, IDs, ordem e partições foram preservados; as novas features têm zero ausências e zero infinitos. A lista explícita de 42 preditores exclui `id`, `price` e `particao`.
- `df_test` permaneceu bruto (3.005 × 96, colunas textuais) e seu arquivo local `data/processed/df_test_raw.csv` manteve o tamanho registrado de 11.634.013 bytes. Nenhum modelo ou MAPE foi calculado nesta etapa; ganho preditivo ainda precisa ser demonstrado em validação.
- **Decisão:** manter as 22 novas features como candidatas auditáveis. O centro espacial deve ser reproduzido a partir do treino; categorias raras e correlações altas exigem atenção nas etapas de seleção e preparo.
- **Pendências:** aprovação do dicionário e das regras contra vazamento no gate da Etapa 03. Última etapa aprovada: Etapa 02. Não iniciar a Etapa 04 antes dessa aprovação.
