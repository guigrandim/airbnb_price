# Revisão do projeto antes da Etapa 11

Data: 15/11/2026. Status: revisão concluída; alterações metodológicas propostas, não implementadas. Último gate aprovado: Etapa 09; gate financeiro da Etapa 10 pendente.

## Objetivo e escopo

Auditar o projeto com um subagente independente, aprofundando Data Quality e EDA. Conferir seleção de colunas, exclusões, joins, outliers, vazamento, avaliação e reprodução. A autorização permite reexecutar o notebook quando necessário; não autoriza alterar silenciosamente decisões ou resultados aprovados.

## Estratégia

1. Ler notebook, planos, dependências e resultados salvos; confrontar revisão independente com as fontes.
2. Confirmar leitura/execução MCP e estado real do kernel com uma célula de diagnóstico.
3. Auditar todas as colunas da base principal apenas nos IDs congelados de treino; examinar faltantes, atributos omitidos, remoções e extremos.
4. Confrontar a EDA com esses resultados e identificar experimentos candidatos. Nenhum ajuste supervisionado ou escolha usa o teste.
5. Registrar problemas concretos, limites conhecidos e requisitos futuros separadamente; não avançar à Etapa 11.

## Células e aceite

- Bloco Markdown de revisão e diagnóstico de kernel.
- Blocos sequenciais de auditoria de qualidade e EDA somente no treino.
- Aceite: achados com evidência e referência; distinguir erro de limitação; preservar partições e hash do teste; registrar qualquer impedimento de reprodução; não declarar que um conjunto é melhor sem comparação em treino/CV.

## Achados preliminares confirmados

- Célula Boruta usa listas definidas depois: 131 antes de 133, nos índices originais desta revisão.
- Salvaguarda 14 exige teste já existente; célula 15 o sobrescreve em cada execução. Na reprodução anterior o hash ficou igual.
- Corte de ausências na célula 44 usa snapshot completo, incluindo teste; limite histórico de independência já registrado na Etapa 02.
- OOF ajusta estimador e pré-processamento por fold, mas as escolhas de features/hiperparâmetros foram feitas antes; é diagnóstico interno, não validação aninhada do procedimento completo.
- Teste avaliado cobre 2.562 de 3.005 anúncios; 443 excluídos. MAPE Q1 41,20%; quartos compartilhados 106,90%, com apenas cinco casos. Cobertura da faixa foi medida somente globalmente.
- Pipeline final recebe 40 features prontas; engenharia, centro geográfico, referência temporal e quantis precisam integrar o contrato futuro do aplicativo.
- EV/ROI dependem de premissas ainda ausentes. ΔGMV proxy não prova uplift causal.

## Gate

Revisão concluída. Recomenda-se revisar a população e comparar alternativas no treino antes da Etapa 11. Nenhuma mudança de modelagem ou aprovação da Etapa 11.

## Evidências executadas via MCP

O kernel estava novo: Python 3.10.4, sem DataFrames ou modelo aprovado em memória. Foram inseridas e executadas três células de auditoria na seção final do notebook: diagnóstico de ambiente, cobertura de dados e EDA complementar. Não foi necessário repetir Boruta/Optuna para identificar os problemas de qualidade. Esta revisão não equivale a uma nova execução integral nem a uma comparação de desempenho de modelos.

- Diagnóstico: `e3f85504-8bb8-47e2-a61b-dd76bf23ae44`.
- Cobertura: `831e1fff-cc7b-497a-827f-3485f5f004c8`.
- EDA complementar: `c2c5b0cc-cb31-457e-a349-f34857e9a44a`.
- IDs reconstruídos pelo mesmo algoritmo e seed: 20.030 no snapshot, 14.021 no treino, IDs únicos. Só preços do treino foram usados.
- SHA-256 do teste confirmado antes e depois: `12b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178`.

## Etapa 02 — Data Quality

### Prioridade alta: cobertura e seleção de população

A limpeza atual elimina todos os anúncios sem avaliações. No treino bruto existem 1.652; entre os casos completos, nenhum. Na auditoria MCP, após preço positivo e banheiros preenchidos menores que 10, foram comparados 14.011 anúncios: 12.187 completos e 1.824 incompletos. As medianas de preço foram €125 e €135; as médias €147,89 e €176,99. O filtro inicial desta auditoria exclui seis banheiros ausentes, por isso seus denominadores diferem do resumo independente do subagente que inclui essas seis linhas. Não são contagens finais de todas as regras da Etapa 02.

As maiores ausências no treino original são rating (1.816; 12,952%) e reviews_per_month (1.664; 11,868%). Excluir linhas por qualquer ausência muda o público do modelo para anúncios com histórico. Isso foi autorizado anteriormente, mas limita o produto. Imputadores no pipeline não demonstram desempenho em públicos excluídos da avaliação.

Proposta: experimento separado preservando anúncios com alvo válido e tratando ausência de preditores dentro dos folds. Distinguir sem histórico, sem evento recente e ausência inesperada; não transformar nota ausente em zero. Comparar cobertura, MAPE, MAE e viés nos grupos com/sem histórico e na interseção de casos usados pelo baseline. Não substituir o baseline aprovado sem decisão explícita.

### Prioridade média: inventário de colunas

O corte <30% foi aplicado a uma lista prévia de 18 candidatas, não a uma avaliação de utilidade de todas as 96 colunas. No treino:

| Candidata | Ausências | Encaminhamento |
|---|---:|---|
| beds | 5; 0,036% | Validar domínio e testar camas por hóspede |
| bed_type | 0 | Examinar categorias raras |
| amenities | 0 células vazias | Auditar conteúdo vazio, parser e aliases antes de criar flags |
| guests_included / extra_people | 0 | Verificar significado da diária e disponibilidade na inferência |
| cancellation_policy | 0 | Testar informação incremental |
| calculated_host_listings_count | 0 | Comparar definição com contagem atual |
| host_identity_verified / host_has_profile_pic | 3 cada | Candidatas secundárias |
| cleaning_fee | 2.568; 18,315% | Tratar vazio e taxa separada da diária |
| Seis notas componentes | 13,009%–13,066% | Conferir escala, redundância e uso no instante da previsão |
| security_deposit | 4.343; 30,975% | Não passa o corte vigente; só reconsiderar por decisão explícita |

Não incorporar IDs, URLs, dados pessoais, preço semanal/mensal ou preços do calendário. Texto livre pode ficar fora do MVP por custo e auditabilidade. Boa disponibilidade não comprova ganho preditivo.

### Extremos e joins

- Treino: banheiros 100,5; 15; 10 em anúncios de quatro hóspedes e um quarto sustentam suspeita contextual de cadastro. A queda de skew não prova erro. Proposta experimental: invalidar somente o campo e imputar no treino, comparando com exclusão da linha. Não corrigir automaticamente para 1 ou 1,5.
- bathrooms=0 ocorre em contextos diferentes, inclusive barcos e quartos; não há evidência suficiente para exclusão automática.
- maximum_nights=9999 foi excluído por decisão explícita do usuário, mas não está demonstrado como erro; 1125 também não foi confirmado como default. Uma análise alternativa pode comparar flags/representação robusta, sem restaurar silenciosamente a linha.
- Preços €8.500, €5.040 e €5.000 são atípicos para o contexto, sem prova conclusiva de erro. Preservar e mostrar influência em vez de eliminar apenas por IQR.
- Revisão independente confirmou agregação de reviews por eventos e merge one-to-one. Não deduplicar listing_id+date: avaliações distintas podem ocorrer no mesmo dia. O controle correto é o ID da avaliação, se disponível. A divergência para number_of_reviews permanece diagnóstico, não substituição automática.

## Etapa 04 — EDA

As cinco hipóteses existentes usam treino e interpretação sem causalidade. O principal limite é descreverem a população filtrada. A revisão futura deve repetir hipóteses nessa população ampliada, examinar padrões de ausência e retenção por tipo/bairro/capacidade e contexto dos extremos.

Na auditoria complementar MCP, na coorte de 14.011 anúncios, Spearman com price foi: accommodates 0,551; bedrooms 0,497; beds 0,495; cleaning_fee 0,448; contagem exploratória de amenities 0,212; guests_included 0,198; camas por hóspede 0,185. As amostras variam: cleaning_fee tem 11.448 observações, beds 14.006. Correlações não medem contribuição incremental e podem refletir capacidade/tipo.

Medianas por política de cancelamento: flexible €115; moderate €125; strict_14_with_grace_period €138; super_strict_60 €350, com apenas 34 casos. Isso sugere hipóteses para validação, não causalidade ou escolha automática. O parser exploratório de comodidades usa separador/termos simples e não é uma implementação aprovada.

## Etapa 03 — Feature Engineering após a revisão

Não é possível afirmar que o conjunto atual seja o melhor sem comparar alternativas. Recomenda-se esta ordem:

1. Decidir população e regras de ausências na Etapa 02.
2. Auditar as novas candidatas na EDA do treino.
3. Comparar blocos interpretáveis: camas/capacidade; comodidades; condições comerciais; anfitrião; reputação com estados de ausência.
4. Comparar conjunto simples contra as 40 features atuais e contra blocos ampliados, usando folds e orçamento fixos de treino. Não adicionar tudo de uma vez nem decidir pelo teste conhecido.

Manter distinção entre anúncio sem histórico e zero reviews recentes. Recência ausente precisa de indicador e imputação treinada, não data inventada. As notas componentes exigem verificação de escala. `review_scores_value` representa percepção de valor e deve ter disponibilidade e interpretação examinadas; não é automaticamente informação futura.

Há redundância entre booleanos t/f e flags, contagens e logs, rating×superhost e superhost. Para árvores, logaritmos monotônicos não trazem informação nova por si sós. Comparar ablação em treino antes de remover. O centro geográfico aprendido no treino inteiro fica fora da CV; fixar referência externa documentada ou estimar por fold para avaliação estrita. Preservar snapshot 2018 e fórmulas iguais na inferência.

## Outros achados e prioridades

| Prioridade | Achado | Ação recomendada |
|---|---|---|
| Alta antes de executar linearmente | Listas Boruta definidas após uso | Reordenar pré-requisito e verificar em kernel limpo |
| Alta para reprodução | Teste regravado e salvaguarda exige arquivo existente | Separar criação inicial de verificação; impedir substituição divergente |
| Média metodológica | Corte de ausências usa snapshot inteiro | Registrar contato histórico com teste; futuras decisões aprendidas só no treino |
| Média | OOF com escolhas anteriores feitas no desenvolvimento | Tratar como diagnóstico interno e faixa empírica, sem garantia conformal |
| Alta para produto | Q1 MAPE 41,20%; shared room n=5, MAPE106,90% | Política de elegibilidade/abstenção e ressalvas por segmento |
| Média para produto | Faixa 90,20% avaliada apenas globalmente | Não prometer cobertura por segmento/indivíduo |
| Alta para produto | Referência de €0 após previsão negativa | Definir abstenção; conservar métrica bruta aprovada |
| Alta na Etapa 11 | Pipeline recebe features prontas | Contrato de engenharia, esquema, centro, snapshot e quantis junto ao modelo |
| Baixa | Planos04/05 e docs/index têm status antigo; src contém templates | Atualizar documentação e evitar comandos que anunciam sucesso sem treinar |
| Gate financeiro | Monetização, adoção, demanda, custos e população legal ausentes | Manter EV/ROI pendentes; total OOF+teste é cenário ilustrativo |

## Limites e próximo passo

Revisão com subagente e execução nova de diagnósticos no MCP; sem retreinar ou repetir tuning. Não foi implementada uma população nova nem demonstrado ganho de MAPE. As partições e o teste permanecem congelados; o teste já observado não pode voltar a ser chamado de avaliação inédita após novas escolhas. Para uma versão revisada, decidir previamente como obter evidência independente adicional e usar treino/CV no desenvolvimento.

Recomendação: aprovar um plano de revisão das Etapas 02→EDA complementar→03 e comparação de alternativas, mantendo os resultados atuais como baseline. Não iniciar Streamlit antes dessa decisão.
