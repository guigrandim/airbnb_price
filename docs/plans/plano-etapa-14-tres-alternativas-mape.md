# Etapa 14 — Três alternativas para reduzir o MAPE

## Objetivo, escopo e estratégia

O usuário solicitou testar as três opções propostas após a Etapa 13. Comparar alternativas em desenvolvimento, com 17.021 anúncios, cinco folds com semente 42 e referência V2. O teste histórico fica fora. Conservar hiperparâmetros estruturais e ajustar transformadores no treino de cada fold.

## Blocos previstos

1. **14.1 — Verificação dos pesos.** Comparar perda absoluta com expoentes 0, 0,5 e 1 no peso inverso ao preço. Reusar previsões verificadas da Etapa 13 para expoente 1.
2. **14.2 — Verificação da calibração.** Dentro de cada treino externo, gerar previsões internas em três folds com semente 42. Por faixa de previsão, aprender um multiplicador que minimiza o MAPE interno pela mediana ponderada de preço real dividido pela previsão, com peso previsão/preço real. Usar multiplicador 1 em grupos com menos de 30 exemplos ou previsões não positivas. Aplicar ao generalista no fold externo.
3. **14.3 — Verificação dos atributos.** Acrescentar comodidades disponíveis no snapshot e distância até o décimo vizinho geográfico, usando apenas coordenadas do treino do fold como referência e excluindo a própria linha no treino. Comparar com o V2 usando sua mesma perda.
4. **14.4 — Verificação final.** Comparar resultados globais, por fold e por faixa real. Reportar MAPE, MAE, RMSE, viés, distância até 10% e limites do diagnóstico.

## Critérios de aceite e status

Verificar cobertura completa e previsões finitas. Considerar uma melhora consistente quando o MAPE global cai e melhora em pelo menos quatro folds. Reportar a piora em euros e acima de €175 antes de recomendar uma variante. Executar os blocos via MCP Jupyter. Status inicial em 20/11/2026: execução autorizada.

## Resultados e gate

Os quatro blocos foram executados e inspecionados pelo MCP. Todos os modelos geraram previsões positivas e finitas para os mesmos 17.021 anúncios. A referência V2 teve MAPE de 27,172%.

- Perda absoluta sem pesos: MAPE 23,296% e MAE €37,57. Acima de €175, MAPE 24,533% e viés −€73,93.
- Peso 1/√preço: MAPE 22,415%, MAE €38,81 e RMSE €133,41. Acima de €175, MAPE 27,424% e viés −€90,46. Melhorou cinco folds frente ao V2. O peso integral ficou em 22,432% e foi melhor em três folds frente ao peso intermediário.
- Calibração: MAPE 24,065%, com melhora nos cinco folds frente ao V2. Acima de €175, MAPE 30,024%.
- Comodidades e distância do décimo vizinho: MAPE 27,159%, com melhora em três folds frente ao V2. O bloco combinado teve ganho global de 0,013 ponto percentual.

O melhor MAPE ficou 12,42 pontos percentuais acima de 10%. O desempenho em euros e no segmento caro favorece considerar a perda absoluta sem pesos como candidata de compromisso. O teste histórico ficou fora da comparação. A Etapa 14 está concluída tecnicamente e aguarda aprovação.
