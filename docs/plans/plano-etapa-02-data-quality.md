# Etapa 02: Qualidade e limpeza dos dados

## Objetivo

Revisão V2 autorizada e executada em 15/11/2026: ausências preservadas e cobertura ampliada. Ver [plano e resultados V2](plano-revisao-etapas-02-04-03.md). O conteúdo abaixo registra o baseline histórico; gate V2 pendente.

Auditar o snapshot e montar em memória uma base de desenvolvimento com uma linha por anúncio. Manter o teste bruto reservado para a avaliação final.

## Fonte, seleção e partição

- Base principal: `listings_details.csv`, com 20.030 anúncios, 96 colunas e IDs únicos. Os arquivos brutos permanecem intactos.
- Foram selecionadas 18 features da base principal com menos de 30% de ausências, contando campos vazios e marcadores `N/A`.
- Os 20.030 IDs foram separados no início, por `id` e semente 42: 14.021 treino, 3.004 validação e 3.005 teste. A divisão é aproximadamente 70/15/15.
- Os 20.030 anúncios pertencem aos 22 bairros oficiais de Amsterdam; nenhum foi removido por localização. Outros 49 registros tinham `market` vazio ou diferente de Amsterdam, mas bairro oficial.
- O teste foi salvo sem limpeza em `data/processed/df_test_raw.csv`: 3.005 linhas, 96 colunas textuais e 11.634.013 bytes. A limpeza do modelo considera apenas treino e validação.
- A auditoria inicial consultou o snapshot completo antes da reserva do teste. A partir da decisão de manter o teste bruto, ele ficou fora da exploração e da seleção de features. Não se afirma independência histórica total das decisões anteriores.

## Regras de qualidade aplicadas

- Foram removidos dois anúncios com `price = 0`: IDs `20597844` e `21423332`.
- Três registros de `bathrooms` foram classificados como erros de preenchimento: ID `15199899` (100,5), `16698560` (15) e `17245735` (10). Os dados brutos preservam os valores.
- Os 22 anúncios com `bathrooms = 0` foram mantidos: não há evidência de que zero seja um marcador de ausência.
- Os valores `minimum_nights` de 999 e 1.001 foram mantidos como restrições de estadia longa.
- `maximum_nights = 1.125` aparece em 10.229 de 20.030 anúncios (51,07%). Há 10.783 valores acima de 365, incluindo um valor 9.999 e cinco valores 1.825. Não há conflitos com `minimum_nights`; a documentação não confirma 1.125 nem 9.999 como defaults. Os valores foram mantidos para avaliação como configurações discretas.
- O preço de €2.500 do anúncio `11040717` não foi classificado como erro. O anúncio saiu da base final por ausência em `reviews_per_month` e `review_scores_rating`.
- Após remover os casos acima, foram excluídas 2.214 linhas incompletas de treino e validação.

## Estatísticas e extremos

- A tabela numérica inclui CV amostral, assimetria e curtose excedente de Fisher. O CV é exibido para médias positivas, exceto latitude e longitude.
- `bathrooms` apresentou CV de 69,78%, skew de 98,64 e curtose de 12.264,44. Sem os três valores `>= 10`, o skew cai para 4,23 em 20.017 registros.
- A auditoria de `maximum_nights` não encontrou evidência para remover valores altos nem para tratá-los como defaults.

## Junções de fontes auxiliares

- `reviews.csv` foi agregado por `listing_id` e unido à base de desenvolvimento por `id`, com validação um-para-um. O corte temporal foi 06/12/2018.
- Foram criadas `reviews_last_365d` e `days_since_last_review`. Das 431.830 avaliações da fonte, 371.840 foram associadas aos anúncios de desenvolvimento. Todos os 14.806 anúncios têm histórico na fonte; em 3.557, não houve avaliação na janela de 365 dias e a contagem foi preenchida com zero.
- Não houve datas inválidas, eventos após o snapshot nem ausências nas métricas agregadas. `number_of_reviews` foi preservada, embora divirja da contagem da fonte em 91 anúncios de desenvolvimento.
- Na auditoria do snapshot completo, antes da partição, foram observadas 111 divergências e 18 anúncios com contagem positiva sem eventos correspondentes. Esses números usam uma população diferente.
- `listings.csv` e `neighbourhoods.csv` não acrescentam campos preenchidos úteis. `reviews_details.csv` contém os mesmos eventos e adiciona identificadores pessoais e comentários. `calendar.csv` foi excluído para evitar granularidade diária e preços futuros.

## Resultado

- `df_modeling_final` tem 14.806 linhas e 23 colunas: `id`, `price`, 18 features da base principal, duas métricas agregadas e `particao`.
- Partições: 12.187 treino e 2.619 validação. Não há IDs duplicados, ausências, preços não positivos, bairros fora do escopo, `bathrooms >= 10` ou IDs sem partição.
- A tabela final de modelagem existe apenas em memória. Nenhum CSV foi exportado para ela; `df_test_raw.csv` permanece como o único arquivo salvo para preservar o teste.

## Revisões de decisão e status

- Uma proposta intermediária previa limpar também o teste por uma função. O usuário substituiu essa proposta pela reserva do teste bruto e pela limpeza apenas de treino e validação; nenhuma função foi criada no notebook.
- As contagens anteriores de 17.368 linhas e 2.657 casos incompletos descrevem a proposta anterior à reserva do teste. O resultado vigente é 14.806 linhas de desenvolvimento.
- Gate da Etapa 02 aprovado quando o usuário autorizou a implementação da Etapa 03. Última etapa aprovada: Etapa 02.
- A URL de origem foi dispensada pelo usuário. A licença do arquivo histórico segue sem registro.
- A Etapa 03 foi executada; seu gate ainda aguarda aprovação. Não iniciar a Etapa 04 antes dela.

Notebook: [price_prediction.ipynb](../../notebooks/price_prediction.ipynb).
