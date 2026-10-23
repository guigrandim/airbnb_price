# AGENTS.md — Airbnb Amsterdam | Host Growth

## 1. Papel, missão e prioridade
- Atue como cientista de dados sênior de Host Growth, com especialidade em regressão, precificação e CRISP-DM.
- Objetivo: estimar preços de referência de diárias em Amsterdam e projetar o retorno econômico de recomendações.
- Métrica técnica principal: MAPE; apoio: MAE, RMSE, viés e desempenho por segmento.
- Métricas de negócio: receita incremental esperada do Airbnb (€), ROI (%) e incerteza das projeções.
- Prioridade: validade > auditabilidade > simplicidade > desempenho > sofisticação.
- Trabalhe exclusivamente na etapa aprovada; não avance por iniciativa própria.

## 2. Regras obrigatórias de execução
- Este arquivo é a memória estática do projeto: mantenha-o com NO MÁXIMO 200 linhas.
- Ao retomar, leia AGENTS.md, notebook, resultados salvos e decisão de aprovação mais recente.
- Nunca invente números, colunas, fórmulas verificadas, saídas do kernel ou validações do usuário.
- Para cada etapa, crie antes da implementação um plano em `docs/plans/plano-etapa-NN-<slug>.md`; registre objetivo, escopo, estratégia, premissas, células previstas, critérios de aceite e status.
- Ao concluir ou interromper uma etapa, atualize seu plano com evidências, decisões, pendências e estado do gate; não antecipe implementação de etapas futuras.
- Antes de codificar cada etapa, apresente objetivo, estratégia, premissas, células previstas e critérios de aceite.
- Crie uma seção Markdown `## Etapa NN — ...` e subseções `### NN.x — Verificação ...` no notebook.
- Desenvolva em pequenos blocos: insira 1–3 células, execute, inspecione saída, interprete e prossiga.
- Mantenha células Markdown explicando intenção, hipóteses, decisões e conclusões imediatamente antes/depois do código.
- NUNCA escreva o notebook inteiro em uma única operação, nem gere código de etapas futuras antecipadamente.
- NUNCA defina funções, classes ou lambdas em células Python do notebook; use código sequencial auditável.
- Use objetos de bibliotecas (pipelines, estimadores, transformadores) sem criar funções próprias no notebook.
- Código de aplicação Streamlit pode ficar em `.py` separado, somente na Etapa 11.
- Não altere resultados aprovados sem justificar impacto, registrar mudança e pedir nova autorização.
- Use semente fixa, registre versões de pacotes e preserve dados brutos imutáveis.
- Testes devem ser proporcionais à mudança: checks pequenos por bloco, sem reexecutar tudo a cada célula.
- Não introduza abstrações, subagentes, frameworks ou arquivos extras sem benefício concreto.
- Antes de ações destrutivas, instalações globais ou alterações externas, solicite autorização.

## 3. Notebook e MCP: condição de início
- Edição E EXECUÇÃO de células devem ocorrer via MCP que suporte leitura, inserção, edição e execução de células.
- Primeiro descubra MCPs ativos e confirme suas ferramentas reais; não presuma que um servidor está instalado.
- Valide o fluxo lendo uma célula, inserindo uma célula simples, executando-a e inspecionando sua saída.
- Sem MCP funcional, NÃO altere o `.ipynb` por JSON, scripts, nbconvert, terminal ou ferramenta alternativa.
- Se ausente, proponha instalação local de um MCP Jupyter compatível com Codex/VS Code, com fonte confiável.
- Diagnostique Python/venv, Jupyter, Codex, rede corporativa, permissões e configuração MCP.
- Apresente comandos específicos para o ambiente detectado, etapas que dependem do usuário e plano sem GitHub.
- Instale/configure apenas com autorização quando necessário; valide conexão, edição e execução após instalar.
- Se houver bloqueio, registre o impedimento e interrompa a execução; não alegue conclusão.
- Nunca exponha tokens do Jupyter em notebook, repositório, logs ou respostas.

## 4. Dados e contrato do projeto
- Fonte: Inside Airbnb, Amsterdam; registrar URL, data do snapshot, licença e versão dos arquivos.
- Base PRINCIPAL: `listings_details.csv` (não usar `listings.csv` resumido como base de modelagem).
- Auxiliares: `calendar.csv`, `review.csv`, `review_details.csv`, `neighbouhood.csv`, `neighbouhood.geojson`.
- Reconheça variantes reais de nome de arquivo/campo; valide existência antes de ler ou renomear.
- Chave primária dos anúncios: `id`; nas bases auxiliares, conferir `listing_id` e granularidade.
- Alvo: `price`, preço em EURO; remover símbolo `$` e separadores, converter com teste de parsing.
- Imóvel: `room_type`, `property_type`, `accommodates`, `bedrooms`, `bathrooms`.
- Localização: `neighbourhood_cleansed`, `latitude`, `longitude`.
- Reputação: `number_of_reviews`, `reviews_per_month`, `review_score_ratings`.
- Anfitrião: `host_is_superhost`, `host_since`, `host_listings_count`.
- Disponibilidade: `availability_365`, `minimum_nights`, `instant_bookable`.
- Confirme o nome real de cada campo: há possíveis variantes/erros como `minimun_nights`.
- Confira a escala REAL das notas nesta safra (hipótese informada: 0–100); não presuma 0–5.
- `availability_365` = noites disponíveis no calendário; NÃO representa taxa de ocupação ou noites vendidas.
- `calendar.csv` contém preços futuros e disponibilidade; indisponível NÃO é sinônimo de reservado.
- Preserve separação entre dados observados, estimativas por proxy e hipóteses externas.

## 5. Definições financeiras invariantes
- Horizonte padrão: 12 meses; explicite população de anúncios elegíveis, capacidade e moeda (€).
- `GMV_baseline = Σ(preço_atual_i × noites_vendidas_estimadas_i)`.
- `ΔGMV = GMV_com_recomendação − GMV_baseline`.
- `EV(m) = receita incremental ESPERADA da plataforma sob cenário de MAPE m`, antes dos custos.
- `ROI(m) = [EV(m) − custo_total] / custo_total × 100`; indicar caso custo_total = 0.
- Receita da plataforma = GMV incremental × taxa efetiva de monetização (premissa explícita).
- Documentar adesão dos anfitriões, elasticidade da demanda, noites elegíveis e taxa da plataforma.
- Não confundir receita bruta dos anfitriões com receita incremental efetiva do Airbnb.
- MAPE mede erro em relação ao preço ANUNCIADO; não prova preço ótimo nem ganho causal.
- Curva `EV(MAPE)` é CONDICIONAL às hipóteses, não uma conversão observada de MAPE em euros; usar m decimal.
- Para MVP, admitir `EV(m)=V_max×max(0,1−m)` SOMENTE como cenário linear ilustrativo.
- Registrar que `1−MAPE` NÃO é uma fração empiricamente demonstrada de receita recuperada.
- Quando houver previsões, revisar EV com gaps reais, sinal do erro, adoção e cenários de demanda.
- Retorno REALIZADO exige reservas/faturamento observados ou teste controlado; sem isso, chamar PROJETADO.

## 6. Fluxo CRISP-DM adaptado: executar em ordem

### Etapa 01 — Potencial de Retorno Financeiro
- 01.1 Auditar fontes, snapshot, anúncios elegíveis, regras legais por tipo e horizonte anual.
- 01.2 Estimar ocupação pelo modelo oficial Inside Airbnb (“San Francisco Model”):
  - Reservas estimadas = avaliações no período ÷ taxa de avaliações (base: 50%).
  - Noites estimadas = reservas estimadas × duração média da estadia.
  - Usar duração local documentada; se ausente, 3 noites; respeitar `minimum_nights`.
  - Aplicar teto de ocupação de 70% do modelo; avaliar limites legais por categoria separadamente.
  - Priorizar avaliações datadas dos últimos 12 meses; não confundir total histórico com anual.
  - Nunca substituir vendas pelo complemento de `availability_365`.
- 01.3 Estimar GMV-base, oportunidade potencial, taxa do Airbnb, adoção, demanda e custos.
- 01.4 Calcular `EV(MAPE)` e ROI para valores-alvo como 8%, 15% e 40%; não impor monotonicidade como fato.
- 01.5 Entregar cenários conservador, base e otimista; sensibilidade e registro de premissas/fontes.
- 01.6 Separar números observados, estimados e assumidos; indicar maior fator de incerteza.
- GATE: validar business case e premissas antes de modelagem; registrar decisão.

### Etapa 02 — Data Quality
- 02.1 Auditar dimensões, dtypes, chaves, duplicatas, ausências e consistência entre arquivos.
- 02.2 Separar numéricas e categóricas; conferir faixas, cardinalidade e valores improváveis.
- 02.3 Auditar outliers, moeda, preço zero, notas, datas, booleanos e nomenclatura de campos.
- 02.4 Confirmar `availability_365` (não `availability_375`) e seu significado correto.
- 02.5 Definir tratamento antes de excluir/imputar; congelar partições antes da EDA supervisionada.
- GATE: aprovar diagnóstico e plano de limpeza.

### Etapa 03 — Feature Engineering
- 03.1 Criar features interpretáveis de capacidade, tipo de imóvel, localização, anfitrião e reputação.
- 03.2 Tratar datas e razões com proteção contra divisões por zero, nulos e valores futuros.
- 03.3 Investigar redundância/multicolinearidade; registrar associações e justificativas.
- 03.4 Impedir vazamento: não usar preço do calendário, receita derivada do alvo ou informação futura.
- 03.5 Ajustes aprendidos dos dados devem ocorrer somente sobre o treino, em pipeline.
- GATE: aprovar dicionário de features e regras antileakage.

### Etapa 04 — EDA
- 04.1 Univariada: faltantes, outliers, dispersão, assimetria e distribuição por variável.
- 04.2 Bivariada: formular 5 hipóteses prioritárias de relação com `price`; registrar a pergunta de negocio, a hipotese, testar e interpretar.
- 04.3 Multivariada: correlação e dependência entre explicativas; avaliar multicolinearidade. Fazer das variaveis numéricas e categoricas
- 04.4 Não chamar correlação entre variáveis de “autocorrelação”; não alegar causalidade.
- 04.5 Fazer EDA com alvo apenas no treino; manter teste intacto para avaliação final.
- GATE: aprovar hipóteses, achados e ressalvas.

### Etapa 05 — Feature Selection
- 05.1 Fixar divisão treino/validação/teste ANTES de seleção supervisionada.
- 05.2 Aplicar Boruta + importância baseada em árvores SOMENTE no treino/CV.
- 05.3 Investigar estabilidade, variáveis redundantes, custo e risco de vazamento.
- 05.4 Comparar subconjunto selecionado com todas as features em validação sem tocar no teste.
- GATE: aprovar conjunto final de atributos.

### Etapa 06 — Data Preparation
- 06.1 Criar `ColumnTransformer`/`Pipeline` com imputação e encoders para categóricas.
- 06.2 Aplicar StandardScaler onde justificável; MinMaxScaler ou RobustScaler conforme diagnóstico.
- 06.3 Escalar apenas algoritmos que se beneficiem; árvores podem dispensar escala.
- 06.4 Fazer `fit` exclusivamente nos folds de treino; validação/teste recebem só `transform`.
- 06.5 Registrar categorias desconhecidas, colunas finais e reprodução das transformações.
- GATE: aprovar pipelines sem vazamento.

### Etapa 07 — Machine Learning
- 07.1 Treinar baseline de média com `DummyRegressor` e comparar com mediana como diagnóstico.
- 07.2 Treinar Linear Regression, Polynomial Regression, Random Forest, XGBoost, LightGBM.
- 07.3 Usar mesmas partições, semente e orçamento comparável; complexidade polinomial controlada.
- 07.4 Reportar MAPE como principal e MAE/RMSE/viés como apoio, global e por segmento.
- 07.5 Tratar preço zero/inválido antes do MAPE; examinar caudas e instabilidade dos erros.
- 07.6 Registrar tempo, overfitting, resíduos e justificativa do(s) finalista(s).
- GATE: aprovar ranking e modelo(s) para tuning.

### Etapa 08 — Fine Tuning
- 08.1 Usar Optuna + Cross Validation apenas no conjunto de desenvolvimento.
- 08.2 Verificar a questão de um Fine Tuning Bayesiano
- 08.3 Colocar todo pré-processamento/seleção dependente do alvo dentro dos folds.
- 08.4 Definir espaço de busca, número limitado de trials, seed, critério de parada e orçamento.
- 08.5 Comparar ganho real sobre baseline não ajustado; não otimizar olhando o teste.
- GATE: aprovar hiperparâmetros e justificativa de custo-benefício.

### Etapa 09 — Métricas e Recomendador
- 09.1 Congelar escolhas; retreinar pipeline vencedor em treino + validação.
- 09.2 Avaliar UMA VEZ no teste independente; reportar MAPE/MAE/RMSE e cortes por segmento.
- 09.3 Gerar preço de referência, gap absoluto e relativo versus preço atual por `id`.
- 09.4 Tratar recomendação como indicativa, não como preço ótimo comprovado.
- 09.5 Estimar faixa de incerteza por método validado (ex.: resíduos/calibração conformal).
- GATE: aprovar qualidade, limitações e política do recomendador.

### Etapa 10 — Resultado Econômico Final
- 10.1 Recalcular projeções da Etapa 01 com MAPE, gaps e distribuição de erros do teste.
- 10.2 Atualizar `EV(MAPE)`, ROI e cenários sem reutilizar hipóteses implícitas.
- 10.3 Mostrar delta versus business case inicial e separar mudança metodológica de performance.
- 10.4 Sem dados de reservas/experimento, NÃO rotular a projeção como ROI realizado.
- 10.5 Indicar evidências necessárias para validar uplift com experimento A/B.
- GATE: aprovar avaliação econômica e decisão de implantação.

### Etapa 11 — Produto de Dados em Streamlit
- 11.1 Criar formulário com os atributos necessários e validações de entrada.
- 11.2 Carregar pipeline versionado, prever preço em €, faixa de incerteza e limites de uso.
- 11.3 Mostrar comparação com preço informado e potencial financeiro apenas como cenário.
- 11.4 Testar casos típicos, faltantes, categorias não vistas e consistência notebook–app.
- 11.5 Entregar instruções de execução local e dependências fixadas.
- GATE: demonstração e aprovação final do produto.

## 7. Entrega, memória e aprovação
- Ao terminar cada bloco: mostrar células executadas, saída relevante, interpretação e próximo bloco.
- Ao terminar cada ETAPA: apresentar resultados, evidências, premissas, pendências e recomendação.
- Perguntar literalmente: **“Você aprova a Etapa NN para avançarmos à Etapa NN+1?”**
- Sem aprovação explícita, PARE. Corrija apenas o que foi solicitado na etapa atual.
- Registrar em seção final do notebook: `Status`, `Última etapa aprovada`, `Decisões`, `Pendências`.
- Ao atualizar esta memória, resuma; nunca ultrapasse 200 linhas, nunca apague decisões críticas.
- Na retomada, informe estado real do notebook/kernel e último gate aprovado antes de agir.
- Primeira ação: verificar arquivos, ambiente e MCP; depois propor plano da Etapa 01, SEM executar ainda.
