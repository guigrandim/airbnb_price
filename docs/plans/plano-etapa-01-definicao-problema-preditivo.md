# Etapa 01: Definição do problema preditivo

## Objetivo

Treinar um modelo de regressão que estime o preço anunciado por anúncio no snapshot de Amsterdam.

## Dados e alvo

- Base principal: `data/raw/listings_details.csv`, uma linha por anúncio.
- Snapshot: 6 a 7 de dezembro de 2018, `scrape_id=20181206172549`.
- Alvo: `price`, em euros conforme o contrato do projeto.
- Preditores candidatos: características do imóvel, capacidade, localização, anfitrião e reputação. A seleção final depende das etapas seguintes.
- O problema é transversal ao snapshot. Não é uma previsão de preços para 2027 ou para o mercado atual.

## Métricas

- Principal: MAPE, calculado apenas para preços positivos.
- Apoio: MAE, RMSE, viés e métricas por segmento.

## Evidências

- A base tem 20.030 anúncios, 96 colunas e IDs únicos; os 17 campos candidatos conferidos existem.
- `price` foi convertido em todas as linhas: 20.028 valores positivos, entre €8 e €8.500, e dois zeros.
- O arquivo contém o símbolo `$`; a auditoria registrou que ele é um artefato de exportação, conforme o dicionário do Inside Airbnb consultado.
- A etapa definiu o problema, o alvo, a granularidade, as métricas e os limites. Não treinou nem comparou modelos.

## Limites e decisões

- Preço anunciado não comprova preço ótimo, reservas, causalidade ou receita.
- Não usar preços futuros de `calendar.csv` como preditores.
- Manter o snapshot de 2018 e definir as features após a auditoria de qualidade.

## Status e pendências

- Status: aprovada pelo usuário.
- A URL de origem foi dispensada pelo usuário. A licença do arquivo histórico segue sem registro.
- As seções 01.1 a 01.5 estão em [price_prediction.ipynb](../../notebooks/price_prediction.ipynb).
