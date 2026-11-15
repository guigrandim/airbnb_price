# Etapa 10 V2 — Resultado econômico final

## Status e autorização

Etapa 09 V2 aprovada pelo usuário em 15/11/2026. Etapa 10 V2 autorizada. Plano registrado antes da implementação, usando as skills writing-plans e executing-plans. Escopo limitado à atualização da análise econômica existente.

## Objetivo e escopo

Atualizar gaps e cenários de GMV do snapshot de dezembro de 2018 com as previsões congeladas V2. Usar 17.021 previsões OOF de desenvolvimento e 3.005 previsões de teste já calculadas. Manter pipeline, seleção, previsões e arquivo bruto inalterados. DataFrames permanecem em memória, sem exportação.

Arquivos envolvidos são o notebook `notebooks/price_prediction.ipynb`, este plano, o plano histórico da Etapa 10 e o registro de aprovação da Etapa 09 V2.

## Estratégia e premissas

- Conferir objetos, IDs, preços, previsões e hash antes dos cálculos. Não chamar fit ou predict.
- Preservar a política de abstenção para previsão não positiva também nas recomendações OOF. Gaps ausentes nesses casos. Mostrar contagens e calcular cenários sobre referências utilizáveis, com base comparável.
- Construir uma linha por anúncio com origem treino/validação/teste. Reviews até 06/12/2018, janela de 365 dias, sem usar disponibilidade como ocupação.
- Proxy anual herdado da análise anterior, reservas estimadas = reviews/0,50, estadia = max(3, minimum_nights), noites = min(reservas × estadia, 0,70 × 365). Ausência ou domínio inválido em minimum_nights/reviews impede somente o cálculo do proxy nessa linha e deve ser reconciliada. Não preencher com zero silenciosamente.
- GMV-base = soma(preço anunciado × noites estimadas). Cenário de GMV = soma(referência × mesmas noites), aplicação integral ilustrativa. Delta em euros é diferença sob noites constantes, sem estimar reação da demanda.
- Essa população é tecnicamente analisável. Elegibilidade e limites legais por categoria seguem indefinidos. O teto de 70% é somente premissa do proxy. Resultados não constituem projeção operacional para a Amsterdam atual.
- Usar MAPE em decimal na fórmula ilustrativa EV(m)=V_max × max(0,1−m), com valores 8%,15%,MAPE V2 e40%. Sem V_max aprovado, apresentar apenas fatores algébricos.
- Monetização, adoção, demanda, custos e elegibilidade continuam pendentes conforme a Etapa 01 e o plano histórico. Não inventar valores. EV da plataforma e ROI numéricos permanecem indeterminados. ROI com custo zero é indefinido.
- Comparar base V2 com a histórica por IDs, caso os objetos antigos estejam em memória. Separar população comum e adicionada, GMV-base e delta de preço. Se o cache antigo estiver ausente, registrar limitação e usar somente agregados salvos, sem fabricar comparação pareada.
- OOF foi condicionado às escolhas de desenvolvimento e o teste é um holdout histórico já observado. Não apresentar a soma OOF+teste como validação independente ou ganho causal.

## Células previstas e verificações

- [x] Bloco 10.1, Markdown e código de diagnóstico simples. Verificar memória, dimensões e integridade do teste. Esperado 17.021 OOF,3.005teste,IDs disjuntos e hash original.
- [x] Bloco 10.2, Markdown e código de gaps, merge um-para-um, domínio dos insumos e proxy. Mostrar população elegível tecnicamente, exclusões, noites e GMV por partição/total. Conferir soma dos componentes e identidades de GMV.
- [x] Bloco 10.3, Markdown e código de comparação pareada histórica/V2 e fatores EV/V_max. Decompor população comum/adicionada e registrar diferença de método, cobertura e performance. Não confundir delta de preço com receita da plataforma.
- [x] Bloco 10.4, Markdown e código de auditoria final, tabela dos insumos pendentes e verificação de imutabilidade. Esperado hash e previsões iguais aos objetos congelados, nenhuma chamada adicional do modelo.
- [x] Bloco final Markdown com resultados, premissas, pendências, desenho de validação A/B e gate.

## Critérios de aceite

Alinhamento único por ID, mesma ordem dos preços/previsões congelados, sem regressões na política do recomendador. Reconciliação de linhas sem insumos do proxy ou sem referência. Fórmulas e horizonte de12meses explícitos, GMV em euros e noites estimadas separados de vendas observadas. Comparação histórica respeita populações distintas. Nenhum EV/ROI inventado. Notebook salvo com saídas sem erros, hash original preservado e etapa11aguarda aprovação.

## Gate e pendências

Etapa10V2 aprovada pelo usuário em15/11/2026, com autorização para Etapa11V2. EV/ROI numéricos e decisão econômica de implantação permanecem em aberto por falta de insumos aprovados e evidência causal.

## Evidências da execução

- Célula323 confirmou objetos em memória,17.021OOF e3.005teste,IDs únicos e disjuntos,preços alinhados e hash original. Nenhuma referência OOF não positiva. Detalhamento econômico histórico ausente.
- Célula325 reuniu20.026anúncios. Zero linhas sem insumos válidos do proxy e zero sem referência.6.675sem reviews anuais receberam zero noites pelo proxy. Isso não comprova ausência de vendas.
- Gap mediano combinado€6,90,gap absoluto mediano€24,018,gap percentual mediano5,812% e referência acima do anunciado em58,888%. Teste gap mediano€6,801 e referência acima em58,702%.
- Total858.398,5noites proxy,GMV-base€117.219.415,50,cenário€119.273.047,29,delta+€2.053.631,79. Desenvolvimento usou OOF. Teste123.334noites,base€17.881.593,50,cenário€17.562.161,79,delta−€319.431,71.
- Célula327 comparou somente agregados históricos confirmados na saída241. População+2.659,noites+3.035,GMV-base+€626.639,50,delta de preço+€169.120,94. Sem detalhamento anterior,não foi feita decomposição pareada nem atribuição isolada ao desempenho.
- Seis anúncios com minimum_nights superior ao teto anual do proxy concentram€799.715,00deGMV-base e−€726.819,11dedelta. Quatro têm zero noites pelo proxy. Sensibilidade sem os seis resulta em delta+€2.780.450,90. Não houve exclusão no dataset.
- O anúncio de teste28651212,preço€3.000,mínimo365noites,10reviews anuais,atinge255,5noites no proxy e contribui−€734.238,72ao delta. O rateio de estadias longas e os limites legais não são resolvidos por esse proxy herdado. A concentração limita interpretação econômica.
- Fatores algébricos EV/V_max de0,92;0,85;0,740171;0,60paraMAPE8%,15%,25,982944%,40%. Sem V_max aprovado,nenhumEVem euros. Cenários conservador/base/otimista indicam premissas necessárias,sem valores arbitrários.
- Célula329 verificou domínios,identidades deGMV,alinhamento dos preços/previsões,cópias intactas e SHA-256antes/depois12b7dada5382fdc869754a1abfaf067c5385fd8088bdf56de3bf8764080d1178. Auditoria válida. Nenhum fit ou predict novo.
- Célula330 documenta resultados,concentração,limites,insumos financeiros e desenho futuro de experimento por anfitrião. Nenhuma implementação da Etapa11.

## Decisões e limites

Revisão independente das células322–329 e plano sem problema material. As pendências editoriais apontadas pelo revisor foram fechadas com checklist atualizado e célula330 de síntese,A/B e gate. Verificação final confirmou331células salvas, quatro blocos de código executados sem erros,sem funções/classes/lambdas próprias e sem chamadas fit/predict ou exportação. Hash original preservado e git diff --check sem erros de whitespace.

Usar o proxy herdado para comparabilidade e mostrar sua sensibilidade. Não converter gaps em receita causal. Não alterar o modelo olhando o teste ou excluir anúncios por efeito sobre resultado econômico. A comparação histórica está limitada aos agregados salvos. O holdout histórico já observado e OOF condicionado às escolhas anteriores seguem como ressalvas.

Os cálculos foram concluídos até o limite dos dados disponíveis. EV,ROI,cenários financeiros numéricos e comparação com metas da Etapa01 não podem ser fechados sem os insumos ausentes. Isso exige decisão explícita sobre o gate e não constitui validação econômica de implantação.
