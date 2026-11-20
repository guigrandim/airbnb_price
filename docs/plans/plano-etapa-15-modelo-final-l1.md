# Etapa 15 — Modelo final com perda absoluta

O usuário escolheu o LightGBM com perda absoluta sem pesos e autorizou treinar, salvar o pickle e atualizar o README. A escolha encerra a comparação da Etapa 14.

Usar as 36 variáveis e os hiperparâmetros estruturais do V2. Ajustar o pré-processamento e o estimador L1 nos 17.021 anúncios de desenvolvimento. Recalcular os quantis de erro com as previsões OOF da variante escolhida. Preservar o pickle V2 histórico e apontar a aplicação para o novo artefato versionado.

- **15.1 — Verificação do ajuste e da exportação.** Confirmar população, esquema e previsão finita após reabrir o pickle. Registrar versões, métricas OOF e quantis próprios do L1.
- **15.2 — Verificação da entrega.** Conferir carga pelo módulo de inferência, atualizar o texto do Streamlit e distinguir no README as métricas OOF do L1 dos números históricos do V2. O teste histórico fica fora do novo ajuste e da avaliação.

Status: entrega concluída. O MCP treinou e exportou o pickle L1 com 1.804.075 bytes. A serialização preservou as previsões da amostra de conferência. A carga pelo módulo de inferência confirmou o objetivo regression_l1 e as 36 variáveis. MAPE OOF de 23,2956% e quantis de resíduos real menos previsto de −€53,90 e +€99,76. Aplicativo e README atualizados.
